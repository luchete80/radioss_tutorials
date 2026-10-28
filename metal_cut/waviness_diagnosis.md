# Tool edge waviness diagnosis

The sawtooth edge in the result view is elastic tool deformation, not a bad rigid transform or a visibly nonplanar source edge.

Evidence:

- The source tool's right edge follows `x + 0.2 * (y - 0.004) = 0`. Its 24 boundary nodes deviate by at most `9.19e-9 m` from that plane in `model_0000.rad`.
- The previous coordinate transform's maximum numerical error was about `5e-15 m`, far below the edge deviation and the scale visible in the screenshot.
- In the `t = 0.0004` result, tool nodes move by different amounts in X: node 64421 by `1.57541e-5 m`, 64429 by `1.28918e-4 m`, and 64430 by `5.885e-5 m`.
- `/IMPVEL/1` prescribes X velocity through group 3, which covers only part of the tool. `/BCS/5` constrains Y and Z for the tool nodes, while the tool material is elastic. Nodes without the same X prescription can therefore deform the edge.

`transform_tool.py --uniform-tool-motion` now redirects the existing `/IMPVEL/1` curve to a new node group containing all 196 `/BRICK/2` nodes. It checks that `/BCS/5` contains those nodes and constrains Y and Z only. The generated `model_tool_rot10_dy5e-4_0000.rad` uses group 103 and retains the original material, curve, and boundary conditions. Coordinate cards now use fixed-width scientific notation with 13 significant digits.

Parent solver validation: Starter reported 0 errors; Engine completed normally at t=0.0004 s (801 cycles). The Displacement vector field confirms identical X displacement for all 196 tool nodes: 0.000105 m, spread 0.0 m. Y and Z displacements remain zero. Existing warnings about initial penetrations and incompatible conditions remain; this validates the tool motion, not the complete cutting simulation. Test artifacts: /tmp/metal_cut_uniform_audit_oed1nui4.
