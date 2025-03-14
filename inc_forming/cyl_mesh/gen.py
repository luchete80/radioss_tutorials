import gmsh
import numpy as np


### ld²=2 l²
### ld = sqrt(2)l


def create_mesh(l = 1.0, lc=0.1, r_outer=1.2, r_large=10.0, export_geo=True):
    gmsh.initialize()
    gmsh.model.add("diamond_to_circle")

    geo_content = "// Gmsh geometry file\n"

    # Define the center of the geometry as Point(0)
    center_tag = gmsh.model.geo.addPoint(0, 0, 0, lc)
    geo_content += f"Point({center_tag}) = {{0, 0, 0, {lc}}};\n"
    
    
    # Define the central diamond (square rotated 45 degrees)
    diamond_points = []
    ld = np.sqrt(2.0)*l/2.0
    la = np.cos(np.pi/4.0)/2.0 * l
    coords = [(ld, 0), (la, la),(0,ld), (-la, la),(-ld,0), (-la, -la),(0,-ld), (la, -la)]  # Store actual coordinates
    for x, y in coords:
        tag = gmsh.model.geo.addPoint(x, y, 0, lc)
        diamond_points.append(tag)
        geo_content += f"Point({tag}) = {{{x}, {y}, 0, {lc}}};\n"
        print ("x,y", x,y)

    radial_points = []
    a = 0.0
    ainc = np.pi/4.0
    for x, y in coords:
        print ("angle",a)
        print ("x,y",np.cos(a)*r_outer, np.sin(a)*r_outer)
        tag = gmsh.model.geo.addPoint(np.cos(a)*r_outer, np.sin(a)*r_outer, 0, lc)
        radial_points.append(tag)
        geo_content += f"Point({tag}) = {{{np.cos(a)*r_outer}, {np.sin(a)*r_outer}, 0, {lc}}};\n"
        a += ainc

    #x_, y_ = np.cos(a)*r_large, np.sin(a)*r_large
    ext_radial_points = []
    a = 0.0
    ainc = np.pi/4.0
    for x, y in coords:
        x_, y_ = np.cos(a)*r_large, np.sin(a)*r_large
        tag = gmsh.model.geo.addPoint(x_, y_, 0, lc)
        ext_radial_points.append(tag)
        geo_content += f"Point({tag}) = {{{x_}, {y_}, 0, {lc}}};\n"
        a += ainc

   ######################################################### LINES #################################################
        
    # Create radial extension lines
    a = 0
    ainc = np.pi/4.0
    radial_lines = []
    for i in range(8):
        tag = gmsh.model.geo.addLine(diamond_points[i], radial_points[i])
        radial_lines.append(tag)
        geo_content += f"Line({tag}) = {{{diamond_points[i]}, {radial_points[i]}}};\n"


    # Create lines for the inner diamond
    diamond_lines = []
    for i in range(8):
        j = i + 1
        if (j==8): j ==0
        tag = gmsh.model.geo.addLine(diamond_points[i], diamond_points[(i + 1) % 8])
        diamond_lines.append(tag)
        geo_content += f"Line({tag}) = {{{diamond_points[i]}, {diamond_points[(i + 1) % 8]}}};\n"

    arc_lines = []
    for i in range(8):
        j = i + 1
        if (j==8):
          j = 0
        tag = gmsh.model.geo.addCircleArc(radial_points[i], center_tag, radial_points[j])
        arc_lines.append(tag)
        geo_content += f"Circle({tag}) = {{{radial_points[i]}, {center_tag}, {radial_points[j]}}};\n"

    # Create loop for the central square
    square_loop = gmsh.model.geo.addCurveLoop(diamond_lines)
    geo_content += f"Curve Loop({square_loop}) = {{{', '.join(map(str, diamond_lines))}}};\n"


    # Create loops for the transition regions
    transition_loops = []
    for i in range(8):
        print ("CURVE LINES ", diamond_lines[i], radial_lines[(i + 1) % 8], -arc_lines[i], -radial_lines[i])
        tag = gmsh.model.geo.addCurveLoop([
            diamond_lines[i], radial_lines[(i + 1) % 8], -arc_lines[i], -radial_lines[i]
        ])
        transition_loops.append(tag)
        geo_content += f"Curve Loop({tag}) = {{{diamond_lines[i]}, {radial_lines[(i + 1) % 8]}, {-arc_lines[i]}, {-radial_lines[i]}}};\n"


    # Create surfaces
    square_surface = gmsh.model.geo.addPlaneSurface([square_loop])
    transition_surfaces = [gmsh.model.geo.addPlaneSurface([loop]) for loop in transition_loops]

    geo_content += f"Plane Surface({square_surface}) = {{{square_loop}}};\n"
    for i, loop in enumerate(transition_loops):
        geo_content += f"Plane Surface({transition_surfaces[i]}) = {{{loop}}};\n"

    # Apply Transfinite Meshing
    all_surfaces = [square_surface] + transition_surfaces

    for i, surface in enumerate(all_surfaces):
        gmsh.model.geo.mesh.setTransfiniteSurface(surface)
        geo_content += f"Transfinite Surface({surface});\n"

    for line in diamond_lines + radial_lines + arc_lines:
        gmsh.model.geo.mesh.setTransfiniteCurve(line, 10)  # Adjust divisions as needed
        geo_content += f"Transfinite Curve{{{line}}}= 10;\n"

    # Optional: Recombine surfaces to get quadrilateral elements
    for surface in all_surfaces:
        gmsh.model.geo.mesh.setRecombine(2, surface)
        geo_content += f"Recombine Surface({surface});\n"

    #gmsh.model.mesh.generate(2)

    # Save mesh and geometry files
    gmsh.write("diamond_to_circle.msh")
    if export_geo:
        with open("diamond_to_circle.geo", "w") as f:
            f.write(geo_content)
        
 
    gmsh.finalize()

# Run the mesher and export .geo
create_mesh()






