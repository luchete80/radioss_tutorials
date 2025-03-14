lc = 1.0;

// Define points
Point(1) = {0, 0, 0, lc};
Point(2) = {4, 0, 0, lc};
Point(3) = {6, 3, 0, lc};
Point(4) = {0, 3, 0, lc};

// Define lines
Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 1};

// Set transfinite curves
Transfinite Curve {1} = 6;  // 10 nodes along Line 1
Transfinite Curve {3} = 6;   // 6 nodes along Line 3
Transfinite Curve {2} = 7;   // 7 nodes along Line 2
Transfinite Curve {4} = 7;   // 7 nodes along Line 4

// Define surface
Line Loop(5) = {1, 2, 3, 4};
Plane Surface(6) = {5};

// Apply transfinite mesh
Transfinite Surface {6};
Recombine Surface {6}; // Convert triangles to quads

Mesh 2;
