import gmsh
import numpy as np

def create_mesh(l = 1.0, lc=0.1, r_outer=1.2, r_large=10.0, export_geo=True):
    gmsh.initialize()
    gmsh.model.add("diamond_to_circle")

    geo_content = "// Gmsh geometry file\n"

    # Define the center of the geometry as Point(0)
    center_tag = gmsh.model.geo.addPoint(0, 0, 0, lc)
    geo_content += f"Point({center_tag}) = {{0, 0, 0, {lc}}};\n"
    
    
    # Define the central diamond (square rotated 45 degrees)
    diamond_points = []
    la = np.cos(np.pi/4.0) * l
    coords = [(la, 0), (0, la), (-la, 0), (0, -la)]  # Store actual coordinates
    for x, y in coords:
        tag = gmsh.model.geo.addPoint(x, y, 0, lc)
        diamond_points.append(tag)
        geo_content += f"Point({tag}) = {{{x}, {y}, 0, {lc}}};\n"
        print ("x,y", x,y)
    # Define radial extension points
    radial_points = []
    for x, y in coords:
        x_, y_ = (x / la)*(r_outer), (y / la)*(r_outer)  # Unit direction
        tag = gmsh.model.geo.addPoint(x_, y_, 0, lc)
        radial_points.append(tag)
        geo_content += f"Point({tag}) = {{{x_}, {y_}, 0, {lc}}};\n"

    
    ### POINTS AFTER MAIN CYLINDER
    # Define radial extension points
    radial_points_cent = []
    for x, y in coords:
        x_, y_ = (x / la)*(r_large), (y / la)*(r_large)  # Unit direction
        tag = gmsh.model.geo.addPoint(x_, y_, 0, lc)
        radial_points_cent.append(tag)
        geo_content += f"Point({tag}) = {{{x_}, {y_}, 0, {lc}}};\n"

    # Define radial extension points
    radial_points_cent_rot = []
    ainc = np.pi/2.0
    a = np.pi/4.0
    for ang in range(4):
        print ("angle",a)
        print ("x,y",np.cos(a)*r_large, np.sin(a)*r_large)
        tag = gmsh.model.geo.addPoint(np.cos(a)*r_large, np.sin(a)*r_large, 0, lc)
        radial_points_cent_rot.append(tag)
        geo_content += f"Point({tag}) = {{{np.cos(a)*r_large}, {np.sin(a)*r_large}, 0, {lc}}};\n"
        a += ainc


    # Create lines for the inner diamond
    diamond_lines = []
    for i in range(4):
        tag = gmsh.model.geo.addLine(diamond_points[i], diamond_points[(i + 1) % 4])
        diamond_lines.append(tag)
        geo_content += f"Line({tag}) = {{{diamond_points[i]}, {diamond_points[(i + 1) % 4]}}};\n"

    # Create radial extension lines
    radial_lines = []
    for i in range(4):
        tag = gmsh.model.geo.addLine(diamond_points[i], radial_points[i])
        radial_lines.append(tag)
        geo_content += f"Line({tag}) = {{{diamond_points[i]}, {radial_points[i]}}};\n"

    # Create radial extension lines
    ext_radial_lines = []
    for i in range(4):
        tag = gmsh.model.geo.addLine(radial_points[i], radial_points_cent[i])
        ext_radial_lines.append(tag)
        geo_content += f"Line({tag}) = {{{radial_points[i]}, {radial_points_cent[i]}}};\n"


    lext_1 = np.pi/4.0 * r_outer/ (l/lc)
    print ("lc outer")
    
    arc_lines = []
    for i in range(4):
        j = i + 1
        if (j==4):
          j = 0
        tag = gmsh.model.geo.addCircleArc(radial_points[i], center_tag, radial_points[j])
        arc_lines.append(tag)
        geo_content += f"Circle({tag}) = {{{radial_points[i]}, {center_tag}, {radial_points[j]}}};\n"

    ### EXTERNAL 
    arc_lines_ext = []
    #FIRST ADD 
    for i in range(4):
        j = i + 1
        if (j==4):
          j = 0
        tag = gmsh.model.geo.addCircleArc(radial_points_cent[i], center_tag, radial_points_cent_rot[i])
        arc_lines_ext.append(tag)
        geo_content += f"Circle({tag}) = {{{radial_points_cent[i]}, {center_tag}, {radial_points_cent_rot[i]}}};\n"
        tag = gmsh.model.geo.addCircleArc(radial_points_cent_rot[i], center_tag, radial_points_cent[j])
        arc_lines_ext.append(tag)
        geo_content += f"Circle({tag}) = {{{radial_points_cent_rot[i]}, {center_tag}, {radial_points_cent[j]}}};\n"

    # Create loop for the central square
    square_loop = gmsh.model.geo.addCurveLoop(diamond_lines)
    geo_content += f"Curve Loop({square_loop}) = {{{', '.join(map(str, diamond_lines))}}};\n"

    # Create loops for the transition regions
    transition_loops = []
    for i in range(4):
        print ("CURVE LINES ", diamond_lines[i], radial_lines[(i + 1) % 4], -arc_lines[i], -radial_lines[i])
        tag = gmsh.model.geo.addCurveLoop([
            diamond_lines[i], radial_lines[(i + 1) % 4], -arc_lines[i], -radial_lines[i]
        ])
        transition_loops.append(tag)
        geo_content += f"Curve Loop({tag}) = {{{diamond_lines[i]}, {radial_lines[(i + 1) % 4]}, {-arc_lines[i]}, {-radial_lines[i]}}};\n"

    # Create loops for the transition regions
    
    #transition_loops_ext = []
    for i in range(4):
        j = i + 1
        if (j==4): j=0
        print ("EXT CURVE LINES ", ext_radial_lines[i], arc_lines_ext[2*i], arc_lines_ext[2*i+1], -ext_radial_lines[j])
        tag = gmsh.model.geo.addCurveLoop([
            ext_radial_lines[i], arc_lines_ext[2*i], arc_lines_ext[2*i+1], -ext_radial_lines[j]
        ])
        transition_loops.append(tag)
        geo_content += f"Curve Loop({tag}) = {{{ext_radial_lines[i]}, {arc_lines_ext[2*i]}, {arc_lines_ext[2*i+1]},{-ext_radial_lines[j]}}};\n"


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

    gmsh.model.geo.synchronize()

    #gmsh.model.mesh.generate(2)

    # Save mesh and geometry files
    gmsh.write("diamond_to_circle.msh")
    if export_geo:
        with open("diamond_to_circle.geo", "w") as f:
            f.write(geo_content)



    ##### AFTER MESHING ABTAIN COORDS
    node_tags, node_coords, _ = gmsh.model.mesh.getNodes()

    # node_tags is a list of node IDs
    # node_coords is a flat list of coordinates [x1, y1, z1, x2, y2, z2, ...]
    # To reshape it to separate coordinates per node:
    num_nodes = len(node_tags)
    node_coords_reshaped = [node_coords[i:i + 3] for i in range(0, len(node_coords), 3)]
    print ("Node count ",num_nodes)
    # Print node coordinates
    for i, coords in zip(node_tags, node_coords_reshaped):
        print(f"Node {i}: {coords}")
        
            
       # Get element connectivity (including quad elements)
    element_types, element_tags, element_node_tags = gmsh.model.mesh.getElements()

    # Print element connectivity
    print("\nElement Connectivity (Quads):")
    for elem_type, tags, nodes in zip(element_types, element_tags, element_node_tags):
        if elem_type == 3:  # Quad elements (GMSH element type for quadrilaterals is 3)
            for i, elem_tag in zip(tags, nodes):
                print(f"Element {elem_tag} has nodes: {nodes}")
            # To print quad node connectivity nicely
            print(f"Quad element {elem_tag}: Nodes: {nodes}")
        
            
    gmsh.finalize()

# Run the mesher and export .geo
create_mesh()






