#!/usr/bin/env python3
"""Rebuild model 4's workpiece as one z-layer and split every XY cell 2x2.

Only static geometry/deck transformations are performed; this script does not
invoke Starter, Engine, or any solver.
"""

from __future__ import annotations

import argparse
import math
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path


FACE_TEMPLATES = (
    (0, 1, 2, 3), (4, 5, 6, 7),
    (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
)
HEX_SIGNS = (
    (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
    (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
)
CARD_RE = re.compile(rb"^\s*/([^/\s]+)(?:/(\S+))?")


def parse_deck(raw: bytes):
    lines = raw.splitlines(keepends=True)
    nodes = {}
    node_lines = {}
    bricks = {1: [], 2: []}
    groups = {}
    cards = []
    active = None
    group_id = None
    node_section = None

    for i, line in enumerate(lines):
        body = line.rstrip(b"\r\n")
        if body.lstrip().startswith(b"/"):
            match = CARD_RE.match(body.lstrip())
            if not match:
                active = None
                group_id = None
                continue
            card = match.group(1).decode("ascii", "ignore").upper()
            arg = match.group(2).decode("ascii", "ignore") if match.group(2) else None
            cards.append((i, card, arg))
            active, group_id = None, None
            if card == "NODE" and arg is None:
                node_section = (i, None)
                active = "NODE"
            elif card == "BRICK" and arg in ("1", "2"):
                active = f"BRICK{arg}"
            elif card == "GRNOD" and arg and arg.upper().startswith("NODE/"):
                try:
                    group_id = int(arg.split("/")[-1])
                    groups[group_id] = {"start": i, "members": set()}
                    active = "GROUP"
                except ValueError:
                    pass
            continue

        if active == "NODE":
            fields = body.split()
            if len(fields) >= 4:
                try:
                    node_id = int(fields[0])
                    coords = tuple(float(v.replace(b"D", b"E").replace(b"d", b"e")) for v in fields[1:4])
                except ValueError:
                    continue
                if node_id in nodes:
                    raise ValueError(f"duplicate node id {node_id}")
                if not all(math.isfinite(v) for v in coords):
                    raise ValueError(f"non-finite node coordinates at id {node_id}")
                nodes[node_id] = coords
                node_lines[node_id] = i
        elif active in ("BRICK1", "BRICK2"):
            fields = body.split()
            if len(fields) >= 9:
                try:
                    values = tuple(int(v) for v in fields[:9])
                except ValueError:
                    continue
                part = int(active[-1])
                bricks[part].append((values[0], values[1:9], i))
        elif active == "GROUP":
            for token in body.split():
                try:
                    groups[group_id]["members"].add(int(token))
                except ValueError:
                    pass

    for j, (start, card, arg) in enumerate(cards):
        end = cards[j + 1][0] if j + 1 < len(cards) else len(lines)
        if card == "NODE" and arg is None:
            node_section = (start, end)
        if card == "BRICK" and arg in ("1", "2"):
            bricks[int(arg)] = [(eid, conn, idx) for eid, conn, idx in bricks[int(arg)] if start < idx < end]
        if card == "GRNOD" and arg and arg.upper().startswith("NODE/"):
            gid = int(arg.split("/")[-1])
            groups[gid]["end"] = end
    return lines, nodes, node_lines, bricks, groups, cards, node_section


def xy_key(point):
    return (round(point[0], 12), round(point[1], 12))


def polygon_area(points):
    return 0.5 * sum(points[i][0] * points[(i + 1) % 4][1] - points[(i + 1) % 4][0] * points[i][1] for i in range(4))


def det3(a, b, c):
    return (a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0]))


def hex_jacobians(coords):
    g = 1 / math.sqrt(3)
    values = []
    for r in (-g, g):
        for s in (-g, g):
            for t in (-g, g):
                dr = [0.0, 0.0, 0.0]
                ds = [0.0, 0.0, 0.0]
                dt = [0.0, 0.0, 0.0]
                for p, (ri, si, ti) in zip(coords, HEX_SIGNS):
                    dnr = ri * (1 + si * s) * (1 + ti * t) / 8
                    dns = si * (1 + ri * r) * (1 + ti * t) / 8
                    dnt = ti * (1 + ri * r) * (1 + si * s) / 8
                    for k in range(3):
                        dr[k] += dnr * p[k]
                        ds[k] += dns * p[k]
                        dt[k] += dnt * p[k]
                values.append(det3(dr, ds, dt))
    return values


def bilinear(points, u, v):
    weights = ((1-u)*(1-v), u*(1-v), u*v, (1-u)*v)
    return tuple(sum(w * p[k] for w, p in zip(weights, points)) for k in range(3))


def interp_parent_ids(corners, u, v):
    eps = 1e-12
    if u in (0.0, 1.0) and v in (0.0, 1.0):
        idx = {(0.0, 0.0): 0, (1.0, 0.0): 1, (1.0, 1.0): 2, (0.0, 1.0): 3}[(u, v)]
        return (corners[idx],)
    if v == 0.0:
        return corners[0], corners[1]
    if u == 1.0:
        return corners[1], corners[2]
    if v == 1.0:
        return corners[3], corners[2]
    if u == 0.0:
        return corners[0], corners[3]
    return tuple(corners)


def split_grid(corners, nodes, next_node_id, cache, generated_parents):
    pts = [nodes[n] for n in corners]
    grid = {}
    uv = (0.0, 0.5, 1.0)
    for j, v in enumerate(uv):
        for i, u in enumerate(uv):
            parents = interp_parent_ids(corners, u, v)
            if len(parents) == 1:
                grid[i, j] = parents[0]
                continue
            if len(parents) == 2:
                key = ("E",) + tuple(sorted(parents))
            else:
                key = ("F",) + tuple(sorted(corners))
            if key not in cache:
                coords = bilinear(pts, u, v)
                cache[key] = next_node_id[0]
                nodes[next_node_id[0]] = coords
                generated_parents[next_node_id[0]] = parents
                next_node_id[0] += 1
            grid[i, j] = cache[key]
    return grid


def format_node(node_id, p):
    fields = (f"{p[0]:20.12e}", f"{p[1]:20.12e}", f"{p[2]:20.12e}")
    if any(len(x) != 20 for x in fields):
        raise ValueError(f"coordinate does not fit 20 columns for node {node_id}")
    return f"{node_id:10d}".encode() + "".join(fields).encode() + b"\n"


def format_brick(eid, conn):
    return (f"{eid:10d}" + "".join(f"{n:10d}" for n in conn) + "\n").encode()


def section_bounds(cards, index):
    start = cards[index][0]
    end = cards[index + 1][0] if index + 1 < len(cards) else None
    return start, end


def write_group(lines, group, members):
    start, end = group["start"], group["end"]
    block = lines[start + 1:end]
    prefix, suffix = [], []
    saw_data = False
    for line in block:
        body = line.split(b"#", 1)[0].strip()
        toks = body.split()
        is_data = bool(toks)
        if is_data:
            try:
                for token in toks:
                    int(token)
            except ValueError:
                is_data = False
        if is_data:
            saw_data = True
        elif not saw_data:
            prefix.append(line)
        else:
            suffix.append(line)
    generated = []
    ordered = sorted(members)
    for offset in range(0, len(ordered), 10):
        generated.append(("".join(f"{n:10d}" for n in ordered[offset:offset + 10]) + "\n").encode())
    lines[start + 1:end] = prefix + generated + suffix
    delta = len(prefix) + len(generated) + len(suffix) - (end - start - 1)
    return delta


def get_group_members(lines, start, end):
    members = set()
    for line in lines[start + 1:end]:
        body = line.split(b"#", 1)[0]
        for token in body.split():
            try:
                members.add(int(token))
            except ValueError:
                pass
    return members


def transform(raw):
    lines, nodes, node_lines, bricks, groups, cards, node_section = parse_deck(raw)
    if node_section is None or not bricks[1] or not bricks[2]:
        raise ValueError("expected /NODE, /BRICK/1, and /BRICK/2 cards")
    if len({eid for eid, _, _ in bricks[1]}) != len(bricks[1]):
        raise ValueError("duplicate /BRICK/1 element ID")

    wp_nodes = {n for _, conn, _ in bricks[1] for n in conn}
    if not wp_nodes <= nodes.keys():
        raise ValueError("workpiece brick references missing nodes")
    zmin = min(nodes[n][2] for n in wp_nodes)
    zmax = max(nodes[n][2] for n in wp_nodes)
    ztol = 1e-12
    if not zmax > zmin:
        raise ValueError("workpiece has zero z-thickness")

    faces = {zmin: {}, zmax: {}}
    owner = {}
    for eid, conn, _ in bricks[1]:
        for template in FACE_TEMPLATES:
            face = tuple(conn[i] for i in template)
            zs = [nodes[n][2] for n in face]
            side = None
            if all(abs(z - zmin) <= ztol for z in zs):
                side = zmin
            elif all(abs(z - zmax) <= ztol for z in zs):
                side = zmax
            if side is None:
                continue
            key = tuple(sorted(xy_key(nodes[n]) for n in face))
            if key in faces[side]:
                raise ValueError(f"duplicate external z-face cell at z={side}: {key}")
            faces[side][key] = face
            if side == zmin:
                owner[key] = eid
    if not faces[zmin] or set(faces[zmin]) != set(faces[zmax]):
        raise ValueError("z=0 and z=max external face topology/XY do not match")

    # Verify the two external skins have matching XY coordinates at every vertex.
    surface_nodes = {n for face_map in faces.values() for face in face_map.values() for n in face}
    lower_xy = {xy_key(nodes[n]) for n in surface_nodes if abs(nodes[n][2] - zmin) <= ztol}
    upper_xy = {xy_key(nodes[n]) for n in surface_nodes if abs(nodes[n][2] - zmax) <= ztol}
    if lower_xy != upper_xy:
        raise ValueError(f"external skins differ in XY: {len(lower_xy ^ upper_xy)} coordinates")

    upper_by_xy = {xy_key(p): n for n, p in nodes.items() if n in wp_nodes and abs(p[2] - zmax) <= ztol}
    if len(upper_by_xy) != len(upper_xy):
        raise ValueError("upper skin contains duplicate XY coordinates")

    old_nodes = dict(nodes)
    generated_parents = {}
    cache = {}
    next_node = [max(nodes) + 1]
    new_bricks = []
    next_eid = max(eid for part in bricks.values() for eid, _, _ in part) + 1
    old_base_ids = set()
    child_area_values = []

    for key, lower_face in faces[zmin].items():
        # The face template is cyclic. Normalize its projected winding to CCW.
        q = list(lower_face)
        qpoints = [nodes[n] for n in q]
        a = polygon_area(qpoints)
        if abs(a) < 1e-16:
            raise ValueError(f"degenerate projected face for base cell {owner[key]}")
        if a < 0:
            q = [q[0], q[3], q[2], q[1]]
        upper_face = faces[zmax][key]
        top_by_xy = {xy_key(nodes[n]): n for n in upper_face}
        top_q = [top_by_xy[xy_key(nodes[n])] for n in q]
        if any(abs(nodes[a][0] - nodes[b][0]) > 1e-12 or abs(nodes[a][1] - nodes[b][1]) > 1e-12 for a, b in zip(q, top_q)):
            raise ValueError("paired skin nodes do not match in XY")

        bottom_grid = split_grid(q, nodes, next_node, cache, generated_parents)
        top_grid = split_grid(top_q, nodes, next_node, cache, generated_parents)
        base_eid = owner[key]
        if base_eid in old_base_ids:
            raise ValueError(f"base element id {base_eid} used for multiple surface cells")
        old_base_ids.add(base_eid)
        for j in range(2):
            for i in range(2):
                quad_bottom = (bottom_grid[i, j], bottom_grid[i + 1, j], bottom_grid[i + 1, j + 1], bottom_grid[i, j + 1])
                quad_top = (top_grid[i, j], top_grid[i + 1, j], top_grid[i + 1, j + 1], top_grid[i, j + 1])
                area = polygon_area([nodes[n] for n in quad_bottom])
                if area <= 0:
                    raise ValueError(f"nonpositive XY child-cell area under base element {base_eid}")
                child_area_values.append(area)
                if i == 0 and j == 0:
                    eid = base_eid
                else:
                    eid = next_eid
                    next_eid += 1
                new_bricks.append((eid, quad_bottom + quad_top))

    expected = len(faces[zmin]) * 4
    if len(new_bricks) != expected:
        raise ValueError(f"generated {len(new_bricks)} bricks, expected {expected}")

    keep_wp_nodes = surface_nodes
    remove_wp_nodes = wp_nodes - keep_wp_nodes
    all_new_brick_nodes = {n for _, conn in new_bricks for n in conn}
    if not all_new_brick_nodes <= set(nodes):
        raise ValueError("generated bricks reference missing nodes")
    if all_new_brick_nodes & remove_wp_nodes:
        raise ValueError("an interior-z workpiece node remains in generated connectivity")
    new_node_ids = set(generated_parents)
    if new_node_ids != all_new_brick_nodes - keep_wp_nodes:
        raise ValueError("generated node orphan/reference audit failed")

    # Inherit each GRNOD membership onto new points only if every interpolation
    # support node belonged to that original set. Existing non-workpiece nodes
    # and all retained external-skin node memberships are preserved.
    updated_groups = {}
    for gid, record in groups.items():
        members = set(record["members"])
        updated = members - remove_wp_nodes
        for nid, parents in generated_parents.items():
            if set(parents) <= members:
                updated.add(nid)
        updated_groups[gid] = updated

    # The BCS/1 support is the y=0 end face; BCS/4 is the existing pair of
    # outer z faces. Confirm their constrained geometric sets survive exactly.
    group1 = updated_groups.get(1, set())
    group4 = updated_groups.get(4, set())
    tol = 1e-11
    expected_group1_wp = {n for n in all_new_brick_nodes if abs(nodes[n][1]) <= tol}
    expected_group4_wp = all_new_brick_nodes
    if group1 & all_new_brick_nodes != expected_group1_wp:
        raise ValueError("GRNOD/1 no longer covers the full preserved y=0 support")
    if group4 & all_new_brick_nodes != expected_group4_wp:
        raise ValueError("GRNOD/4 no longer covers both preserved outer z faces")

    # Static Jacobian audit for all new elements and volume audit for the old
    # and new workpiece mesh. A one-layer mapped brick has straight vertical
    # edges; positivity follows from its projected XY Jacobian.
    min_xy_jac = math.inf
    for (eid, conn) in new_bricks:
        lower = [nodes[n] for n in conn[:4]]
        area = polygon_area(lower)
        dz = nodes[conn[4]][2] - nodes[conn[0]][2]
        if dz <= 0:
            raise ValueError(f"nonpositive thickness in new brick {eid}")
        min_xy_jac = min(min_xy_jac, area / 4)
    old_volumes = [sum(hex_jacobians([nodes[n] for n in conn])) for _, conn, _ in bricks[1]]
    new_jacobians = [hex_jacobians([nodes[n] for n in conn]) for _, conn in new_bricks]
    new_volumes = [sum(values) for values in new_jacobians]
    if any(v <= 0 for v in old_volumes):
        raise ValueError(f"original workpiece has {sum(v <= 0 for v in old_volumes)} nonpositive-volume bricks")
    if any(j <= 0 for values in new_jacobians for j in values):
        raise ValueError("refined workpiece has a nonpositive integration-point Jacobian")

    # Prepare new raw deck by replacing only node, workpiece brick, and affected
    # GRNOD sections. Other cards, including tool, contact, material, and speed,
    # remain byte-for-byte unchanged.
    new_node_lines = []
    for node_id in sorted(new_node_ids):
        new_node_lines.append(format_node(node_id, nodes[node_id]))
    node_start, node_end = node_section
    node_block = lines[node_start + 1:node_end]
    filtered = []
    for line in node_block:
        fields = line.strip().split()
        if fields:
            try:
                old_id = int(fields[0])
            except ValueError:
                old_id = None
            if old_id in remove_wp_nodes:
                continue
        filtered.append(line)
    lines[node_start + 1:node_end] = filtered + new_node_lines

    # Reparse card indices after node-block length changed.
    current_raw = b"".join(lines)
    lines, _, _, _, current_groups, cards, _ = parse_deck(current_raw)
    brick_card_index = next(i for i, (_, card, arg) in enumerate(cards) if card == "BRICK" and arg == "1")
    brick_start, brick_end = section_bounds(cards, brick_card_index)
    lines[brick_start + 1:brick_end] = [format_brick(eid, conn) for eid, conn in new_bricks]

    # Reindex and rewrite only groups whose member set actually changed.
    current_raw = b"".join(lines)
    lines, _, _, _, current_groups, cards, _ = parse_deck(current_raw)
    edits = []
    for gid, record in current_groups.items():
        original = record["members"]
        desired = updated_groups[gid]
        if original == desired:
            continue
        edits.append((record["start"], record["end"], gid, desired))
    # Descending order keeps earlier line offsets stable.
    for _, _, gid, desired in sorted(edits, reverse=True):
        record = current_groups[gid]
        write_group(lines, record, desired)

    result = b"".join(lines)
    # Final referential integrity, element uniqueness, and group membership.
    _, final_nodes, _, final_bricks, final_groups, _, _ = parse_deck(result)
    all_element_ids = [eid for part in final_bricks.values() for eid, _, _ in part]
    if len(all_element_ids) != len(set(all_element_ids)):
        raise ValueError("duplicate element IDs after refinement")
    final_node_ids = set(final_nodes)
    for part in (1, 2):
        for eid, conn, _ in final_bricks[part]:
            missing = set(conn) - final_node_ids
            if missing:
                raise ValueError(f"brick {eid} references missing nodes {sorted(missing)[:8]}")
    for gid, record in final_groups.items():
        missing = record["members"] - final_node_ids
        if missing:
            raise ValueError(f"group {gid} references missing nodes {sorted(missing)[:8]}")

    expected_wp_z = {round(zmin, 12), round(zmax, 12)}
    final_wp_nodes = {n for _, conn, _ in final_bricks[1] for n in conn}
    if {round(final_nodes[n][2], 12) for n in final_wp_nodes} != expected_wp_z:
        raise ValueError("final workpiece does not have exactly one element layer through z")
    if len(final_wp_nodes) != len(final_wp_nodes & {n for _, conn, _ in final_bricks[1] for n in conn}):
        raise ValueError("workpiece node reachability audit failed")
    return result, {
        "old_wp_nodes": len(wp_nodes), "kept_skin_nodes": len(surface_nodes),
        "removed_interior_nodes": len(remove_wp_nodes), "new_nodes": len(new_node_ids),
        "old_wp_bricks": len(bricks[1]), "surface_cells": len(faces[zmin]),
        "new_wp_bricks": len(new_bricks), "groups_changed": sorted(gid for _, _, gid, _ in edits),
        "zmin": zmin, "zmax": zmax, "min_child_area": min(child_area_values),
        "max_child_area": max(child_area_values), "min_xy_jacobian": min_xy_jac,
        "old_total_volume": sum(old_volumes), "new_total_volume": sum(new_volumes),
        "old_min_volume": min(old_volumes), "new_min_volume": min(new_volumes),
        "new_min_jacobian": min(min(values) for values in new_jacobians),
        "old_group_counts": {gid: len(groups[gid]["members"]) for gid in groups},
        "new_group_counts": {gid: len(final_groups[gid]["members"]) for gid in final_groups},
        "final_nodes": len(final_nodes), "final_wp_nodes": len(final_wp_nodes),
        "final_tool_nodes": len({n for _, conn, _ in final_bricks[2] for n in conn}),
        "tool_bricks": len(final_bricks[2]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", nargs="?", type=Path, default=Path("model_0000.rad"))
    parser.add_argument("--backup", type=Path, default=None)
    args = parser.parse_args()
    deck = args.deck.resolve()
    backup = args.backup.resolve() if args.backup else deck.with_suffix(deck.suffix + ".before_xy_refine")
    temp = deck.with_suffix(deck.suffix + ".refining.tmp")
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {backup}")
    raw = deck.read_bytes()
    result, audit = transform(raw)
    shutil.copy2(deck, backup)
    temp.write_bytes(result)
    temp.replace(deck)
    print(f"backup: {backup}")
    print(f"updated deck: {deck}")
    for key, value in audit.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
