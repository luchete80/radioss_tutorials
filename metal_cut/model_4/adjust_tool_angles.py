#!/usr/bin/env python3
"""Apply the measured rake/clearance affine adjustment to a raised tool deck."""

import argparse
import importlib.util
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("transform_tool", ROOT / "transform_tool.py")
transform_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transform_tool)


def apply(raw):
    lines, records, tool_nodes = transform_tool.parse_deck(raw, 2)
    # The model 3 tool's cutting-face angles, measured from its node geometry.
    source_rake = math.radians(21.3098)
    source_clearance = math.radians(1.3087)
    target_rake = math.radians(17.5)
    target_clearance = math.radians(7.0)

    u = (-math.sin(source_rake), math.cos(source_rake))
    v = (-math.cos(source_clearance), math.sin(source_clearance))
    U = (-math.sin(target_rake), math.cos(target_rake))
    V = (-math.cos(target_clearance), math.sin(target_clearance))
    det = u[0] * v[1] - v[0] * u[1]
    m00 = (U[0] * v[1] - V[0] * u[1]) / det
    m01 = (-U[0] * v[0] + V[0] * u[0]) / det
    m10 = (U[1] * v[1] - V[1] * u[1]) / det
    m11 = (-U[1] * v[0] + V[1] * u[0]) / det

    tip_id = 64421
    if tip_id not in tool_nodes:
        raise ValueError("expected model 3 cutting tip node 64421 in /BRICK/2")
    pivot = records[tip_id][1]
    for node_id in tool_nodes:
        line_no, (x, y, z), _, ending = records[node_id]
        dx, dy = x - pivot[0], y - pivot[1]
        nx = pivot[0] + m00 * dx + m01 * dy
        ny = pivot[1] + m10 * dx + m11 * dy
        body = lines[line_no].rstrip(b"\r\n")
        match = re.match(rb"^\s*\S+\s+\S+\s+\S+\s+\S+", body)
        if not match:
            raise ValueError(f"cannot parse coordinates for node {node_id}")
        lines[line_no] = (
            f"{node_id:10d}{nx:20.12e}{ny:20.12e}{z:20.12e}".encode("ascii")
            + body[match.end():]
            + ending
        )
    return b"".join(lines), len(tool_nodes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="raised deck before this angle adjustment")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    result, count = apply(raw)
    args.output.write_bytes(result)
    print(f"adjusted /BRICK/2 nodes: {count}; rake=17.5 deg; clearance=7 deg")
    print(f"output: {args.output}")


if __name__ == "__main__":
    main()
