#!/usr/bin/env python3
"""Translate a Radioss /BRICK part in Y, then rotate about its translated pivot."""

import argparse
import math
import os
import re
import sys


CARD_RE = re.compile(r"^\s*/([^/\s]+)(?:/(\S+))?")


def finite_float(value, label):
    try:
        result = float(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be a number: {value!r}") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def parse_deck(raw, part_id):
    lines = raw.splitlines(keepends=True)
    node_records = {}
    part_nodes = set()
    other_part_nodes = set()
    in_nodes = False
    active_brick = None
    found_node_card = False
    found_target_part = False

    for line_no, line in enumerate(lines):
        body = line.rstrip(b"\r\n")
        if body.lstrip().startswith(b"/"):
            text = body.decode("ascii", errors="ignore")
            match = CARD_RE.match(text)
            card = match.group(1).upper() if match else ""
            arg = match.group(2) if match else None
            in_nodes = card == "NODE" and arg is None
            if in_nodes:
                found_node_card = True
            active_brick = int(arg) if card == "BRICK" and arg and arg.isdigit() else None
            if active_brick == part_id:
                found_target_part = True
            continue

        if in_nodes:
            if not body.strip() or body.lstrip().startswith(b"#"):
                continue
            fields = body.split()
            if len(fields) < 4:
                continue
            try:
                node_id = int(fields[0])
                coords = tuple(float(f.replace(b"D", b"E").replace(b"d", b"e")) for f in fields[1:4])
            except ValueError:
                continue
            if not all(math.isfinite(v) for v in coords):
                raise ValueError(f"non-finite coordinate for node {node_id} on line {line_no + 1}")
            if node_id in node_records:
                raise ValueError(f"duplicate /NODE id {node_id} on line {line_no + 1}")
            # Keep everything after the three coordinates verbatim.
            match = re.match(rb"^\s*\S+\s+\S+\s+\S+\s+\S+", body)
            tail = body[match.end():] if match else b""
            ending = line[len(body):]
            node_records[node_id] = (line_no, coords, tail, ending)
        elif active_brick is not None:
            if not body.strip() or body.lstrip().startswith(b"#"):
                continue
            fields = body.split()
            try:
                values = [int(f) for f in fields]
            except ValueError:
                continue
            if len(values) < 9:
                continue
            nodes = values[1:9]
            (part_nodes if active_brick == part_id else other_part_nodes).update(nodes)

    if not found_node_card:
        raise ValueError("deck has no /NODE card")
    if not found_target_part:
        raise ValueError(f"deck has no /BRICK/{part_id} card")
    if not part_nodes:
        raise ValueError(f"/BRICK/{part_id} contains no readable elements")
    missing = sorted(part_nodes - node_records.keys())
    if missing:
        raise ValueError(f"/BRICK/{part_id} references missing nodes: {missing[:12]}")
    shared = sorted(part_nodes & other_part_nodes)
    if shared:
        raise ValueError(f"part {part_id} shares nodes with another /BRICK part: {shared[:12]}")
    return lines, node_records, part_nodes


def transform(raw, part_id, angle_deg, dy, pivot_node=None):
    lines, records, nodes = parse_deck(raw, part_id)
    if pivot_node is not None:
        if pivot_node not in records:
            raise ValueError(f"pivot node {pivot_node} does not exist in /NODE")
        pivot = records[pivot_node][1]
        pivot_id = pivot_node
    else:
        ymin = min(records[n][1][1] for n in nodes)
        # Scale-aware tolerance: only selects the bottom layer despite roundoff.
        tol = max(1e-12, abs(ymin) * 1e-10)
        bottom = [n for n in nodes if records[n][1][1] <= ymin + tol]
        pivot_id = max(bottom, key=lambda n: records[n][1][0])
        pivot = records[pivot_id][1]

    theta = math.radians(angle_deg)
    c, s = math.cos(theta), math.sin(theta)
    # A pivot belonging to the moving part follows its Y translation.
    # External reference nodes remain fixed with the rest of the model.
    pivot_y = pivot[1] + dy if pivot_id in nodes else pivot[1]
    for node_id in nodes:
        line_no, (x, y, z), tail, ending = records[node_id]
        dx, ddy = x - pivot[0], y + dy - pivot_y
        nx = pivot[0] + c * dx - s * ddy
        ny = pivot_y + s * dx + c * ddy
        # Keep coordinate cards at fixed width while retaining enough digits
        # that a rigid transform does not discard meaningful mesh precision.
        # 12 digits after the decimal yields a 19-character negative value,
        # leaving one blank in the 20-column field so whitespace parsers keep
        # the node ID and coordinate as separate tokens.
        coords = (f"{nx:20.12e}{ny:20.12e}{z:20.12e}")
        if any(len(value) != 20 for value in (f"{nx:20.12e}", f"{ny:20.12e}", f"{z:20.12e}")):
            raise ValueError(f"coordinate does not fit a 20-column field for node {node_id}")
        lines[line_no] = (f"{node_id:10d}{coords}".encode("ascii") + tail + ending)
    return b"".join(lines), pivot_id, pivot, len(nodes)


def patch_uniform_tool_motion(raw, part_id, node_ids):
    """Prescribe the existing X velocity curve to every node in the tool part."""
    lines = raw.splitlines(keepends=True)
    cards = []
    for index, line in enumerate(lines):
        match = CARD_RE.match(line.decode("ascii", errors="ignore").strip())
        if match:
            cards.append((index, match.group(1).upper(), match.group(2)))

    grnod_cards = [(i, int(arg.split("/")[-1])) for i, card, arg in cards
                   if card == "GRNOD" and arg and arg.startswith("NODE/") and arg.split("/")[-1].isdigit()]
    if not grnod_cards:
        raise ValueError("--uniform-tool-motion requires at least one /GRNOD/NODE group")
    group_id = max(gid for _, gid in grnod_cards) + 1

    def group_members(start, end):
        members = set()
        for line in lines[start + 1:end]:
            body = line.split(b"#", 1)[0]
            for token in body.split():
                try:
                    members.add(int(token))
                except ValueError:
                    pass
        return members

    groups = {}
    for index, gid in grnod_cards:
        end = next((j for j, _, _ in cards if j > index), len(lines))
        groups[gid] = group_members(index, end)
    missing_lock = node_ids - groups.get(5, set())
    if missing_lock:
        raise ValueError(f"/BCS/5 group does not contain all /BRICK/{part_id} nodes; missing {len(missing_lock)}")

    bcs5 = next((i for i, card, arg in cards if card == "BCS" and arg == "5"), None)
    if bcs5 is None:
        raise ValueError("--uniform-tool-motion requires /BCS/5 to keep the tool's Y and Z fixed")
    bcs_end = next((j for j, _, _ in cards if j > bcs5), len(lines))
    bcs_line = next((fields for line in lines[bcs5 + 1:bcs_end]
                     if (fields := line.split(b"#", 1)[0].split()) and len(fields) >= 4), None)
    if not bcs_line or len(bcs_line) < 4 or bcs_line[0] != b"011" or bcs_line[3] != b"5":
        raise ValueError("/BCS/5 must constrain Y and Z only (component flags 011) on group 5")

    impvel = next((i for i, card, arg in cards if card == "IMPVEL" and arg == "1"), None)
    if impvel is None:
        raise ValueError("--uniform-tool-motion requires /IMPVEL/1")
    card_end = next((j for j, _, _ in cards if j > impvel), len(lines))
    values_line = None
    for i in range(impvel + 1, card_end):
        if lines[i].strip() and not lines[i].lstrip().startswith(b"#"):
            if len(lines[i].split()) >= 7:
                values_line = i
                break
    if values_line is None:
        raise ValueError("cannot parse /IMPVEL/1 data line")
    tokens = list(re.finditer(rb"\S+", lines[values_line]))
    fields = [m.group() for m in tokens]
    if fields[1].upper() != b"X":
        raise ValueError("/IMPVEL/1 must prescribe the X direction")
    old_group = int(fields[4])
    field = tokens[4]
    card_start = tokens[0].start() - (10 - len(tokens[0].group()))
    field_start = card_start + 4 * 10
    field_end = field_start + 10
    if (field_start < 0 or field.end() > field_end
            or field.start() != field_end - len(field.group())
            or any(m.start() != card_start + i * 10 + (10 - len(m.group())) for i, m in enumerate(tokens[:7]))):
        raise ValueError("/IMPVEL/1 group ID is not in the expected 10-column field")
    lines[values_line] = lines[values_line][:field_start] + f"{group_id:10d}".encode("ascii") + lines[values_line][field_end:]

    end_card = next((i for i, card, _ in cards if card == "END"), None)
    if end_card is None:
        raise ValueError("deck has no /END card for inserting the dedicated tool node group")
    group_lines = [f"/GRNOD/NODE/{group_id}\n".encode("ascii"), b"Uniformly prescribed tool nodes\n"]
    ordered = sorted(node_ids)
    for offset in range(0, len(ordered), 10):
        group_lines.append(("".join(f"{n:10d}" for n in ordered[offset:offset + 10]) + "\n").encode("ascii"))
    lines[end_card:end_card] = group_lines
    return b"".join(lines), old_group, group_id


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="model_0000.rad")
    parser.add_argument("-o", "--output", default=None, help="output deck (default: <input stem>_transformed.rad)")
    parser.add_argument("--angle-deg", required=True, type=lambda x: finite_float(x, "angle-deg"))
    parser.add_argument("--dy", required=True, type=lambda x: finite_float(x, "dy"))
    parser.add_argument("--part", type=int, default=2, help="/BRICK part id (default: 2)")
    parser.add_argument("--pivot-node", type=int, help="Z-axis reference node; a node in the selected part follows its translation, an external node stays fixed")
    parser.add_argument("--uniform-tool-motion", action="store_true", help="apply the existing /IMPVEL/1 X curve to every node in the selected part")
    parser.add_argument("--force", action="store_true", help="replace an existing output file")
    args = parser.parse_args(argv)
    source = os.path.realpath(os.path.abspath(args.input))
    output = os.path.realpath(os.path.abspath(args.output or (os.path.splitext(args.input)[0] + "_transformed.rad")))
    try:
        if source == output or (os.path.exists(output) and os.path.samefile(source, output)):
            raise ValueError("input and output paths must differ")
        if os.path.exists(output) and not args.force:
            raise ValueError(f"output already exists (use --force to replace): {output}")
        with open(source, "rb") as stream:
            raw = stream.read()
        motion_change = None
        if args.uniform_tool_motion:
            _, _, part_nodes = parse_deck(raw, args.part)
            raw, old_group, new_group = patch_uniform_tool_motion(raw, args.part, part_nodes)
            motion_change = (old_group, new_group)
        transformed, pivot_id, pivot, count = transform(raw, args.part, args.angle_deg, args.dy, args.pivot_node)
        # Exclusive creation prevents clobbering a file created after the check.
        mode = "wb" if args.force else "xb"
        with open(output, mode) as stream:
            stream.write(transformed)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"part: {args.part}; transformed nodes: {count}")
    print(f"pivot node: {pivot_id}; pivot coordinates: ({pivot[0]:.12g}, {pivot[1]:.12g}, {pivot[2]:.12g})")
    if motion_change:
        print(f"uniform tool motion: /IMPVEL/1 group {motion_change[0]} replaced by /GRNOD/NODE/{motion_change[1]} ({count} nodes)")
    print(f"output: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
