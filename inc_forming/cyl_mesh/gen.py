import gmsh
import numpy as np


### ld²=2 l²
### ld = sqrt(2)l


def create_mesh(l = 0.04, lc=0.05, r_outer=0.032, r_large=0.18, l_tot = 0.22, export_geo=True):
    gmsh.initialize()
    gmsh.model.add("diamond_to_circle")

    geo_content = "// Gmsh geometry file\n"

    # Define the center of the geometry as Point(0)
    center_tag = gmsh.model.geo.addPoint(0, 0, 0, lc)
    geo_content += f"Point({center_tag}) = {{0, 0, 0, {lc}}};\n"
    
    radial_elem_eigth = (int)(l/lc)
    print (radial_elem_eigth, "radial_elem_eigth")
    #radial_elem_eigth = 10
         
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
    
    ext_sq_point = []
    coords_e = [(l_tot, 0),(l_tot, l_tot), (0, l_tot), (-l_tot, l_tot), (-l_tot, 0),(-l_tot, -l_tot), (0, -l_tot),(l_tot, -l_tot)]
    for x,y in coords_e: 
        tag = gmsh.model.geo.addPoint(x, y, 0, lc)
        ext_sq_point.append(tag)
        geo_content += f"Point({tag}) = {{{x}, {y}, 0, {lc}}};\n"
        
   ######################################################### LINES #################################################

    # Create lines for the inner diamond
    diamond_lines = []
    for i in range(8):
        j = i + 1
        if (j==8): j ==0
        tag = gmsh.model.geo.addLine(diamond_points[i], diamond_points[(i + 1) % 8])
        diamond_lines.append(tag)
        geo_content += f"Line({tag}) = {{{diamond_points[i]}, {diamond_points[(i + 1) % 8]}}};\n"

    #diamond_diags = []
    #for i in range(0,8,2):
    #    print ("i j",i, j)
    #    j = i + 1
    #    tag = gmsh.model.geo.addLine(center_tag, diamond_points[(i + 1)])
    #    diamond_lines.append(tag)
    #    geo_content += f"Line({tag}) = {{{center_tag}, {diamond_points[(i + 1)]}}};\n"
    
    
        
    # Create radial extension lines
    a = 0
    ainc = np.pi/4.0
    radial_lines = []
    for i in range(8):
        tag = gmsh.model.geo.addLine(diamond_points[i], radial_points[i])
        radial_lines.append(tag)
        geo_content += f"Line({tag}) = {{{diamond_points[i]}, {radial_points[i]}}};\n"

    a = 0
    ainc = np.pi/4.0
    for i in range(8):
        tag = gmsh.model.geo.addLine(radial_points[i], ext_radial_points[i])
        radial_lines.append(tag)
        geo_content += f"Line({tag}) = {{{radial_points[i]}, {ext_radial_points[i]}}};\n"

    a = 0
    ainc = np.pi/4.0
    for i in range(8):
        tag = gmsh.model.geo.addLine(ext_radial_points[i], ext_sq_point[i])
        radial_lines.append(tag)
        geo_content += f"Line({tag}) = {{{ext_radial_points[i]}, {ext_sq_point[i]}}};\n"
              
                
        
    arc_lines = []
    for i in range(8):
        j = i + 1
        if (j==8):
          j = 0
        tag = gmsh.model.geo.addCircleArc(radial_points[i], center_tag, radial_points[j])
        arc_lines.append(tag)
        geo_content += f"Circle({tag}) = {{{radial_points[i]}, {center_tag}, {radial_points[j]}}};\n"

    # Create loop for the central square
    #square_loop = gmsh.model.geo.addCurveLoop(diamond_lines)
    #geo_content += f"Curve Loop({square_loop}) = {{{', '.join(map(str, diamond_lines))}}};\n"
    #THIS IS MANUAL
    
  
    #EXTERNAL ARCS
    for i in range(8):
        j = i + 1
        if (j==8):
          j = 0
        tag = gmsh.model.geo.addCircleArc(ext_radial_points[i], center_tag, ext_radial_points[(i+1)%8])
        arc_lines.append(tag)
        geo_content += f"Circle({tag}) = {{{ext_radial_points[i]}, {center_tag}, {ext_radial_points[(i+1)%8]}}};\n"



    sq_lines = []
    for i in range(8):
        tag = gmsh.model.geo.addLine(ext_sq_point[i], ext_sq_point[(i+1)%8 ])
        sq_lines.append(tag)
        geo_content += f"Line({tag}) = {{{ext_sq_point[i]}, {ext_sq_point[(i+1)%8]}}};\n"


    ######################################################################################################
    #SURFACES

    # Create loop for the central square
    square_loop = gmsh.model.geo.addCurveLoop(diamond_lines)
    geo_content += f"Curve Loop({square_loop}) = {{{', '.join(map(str, diamond_lines))}}};\n"
    
    #point_order=[[0,8,11,7],[1,2,9,8]]
    #for i in range(2):
    #    print(diamond_lines[point_order[i,0]])
    #    tag = gmsh.model.geo.addCurveLoop(diamond_lines[point_order[i]])


    # Create loops for the transition regions
    transition_loops = []
    for i in range(8):
        print ("CURVE LINES ", diamond_lines[i], radial_lines[(i + 1) % 8], -arc_lines[i], -radial_lines[i])
        tag = gmsh.model.geo.addCurveLoop([
            diamond_lines[i], radial_lines[(i + 1) % 8], -arc_lines[i], -radial_lines[i]
        ])
        transition_loops.append(tag)
        geo_content += f"Curve Loop({tag}) = {{{diamond_lines[i]}, {radial_lines[(i + 1) % 8]}, {-arc_lines[i]}, {-radial_lines[i]}}};\n"

    for i in range(8):
        j = i + 8 + 1
        if (j==16): j = 8
        print ("CURVE LINES ", arc_lines[i], radial_lines[j], -arc_lines[i+8], -radial_lines[i+8])
        tag = gmsh.model.geo.addCurveLoop([
            arc_lines[i], radial_lines[j], -arc_lines[i+8], -radial_lines[i+8]
        ])
        transition_loops.append(tag)
        geo_content += f"Curve Loop({tag}) = {{{arc_lines[i]}, {radial_lines[j]}, {-arc_lines[i+8]}, {-radial_lines[i+8]}}};\n"

    # TO SQUARE
    print ("EXTERNAL LOOPS")
    for i in range(8):
        k = 8 + i
        j = i + 16 + 1
        if (j==24): j=16
        print ("CURVE LINES ", arc_lines[k], radial_lines[j], -sq_lines[i], -radial_lines[(16+i)%24])
        tag = gmsh.model.geo.addCurveLoop([
            arc_lines[k], radial_lines[j], -sq_lines[i], -radial_lines[(16+i)%24]
        ])
        transition_loops.append(tag)
        geo_content += f"Curve Loop({tag}) = {{{arc_lines[k]}, {radial_lines[j]}, {-sq_lines[i]}, {-radial_lines[(16+i)%24]}}};\n"
        #sq_lines
    #####################################################################################
    #SURFACES
    
    # Create surfaces
    square_surface = gmsh.model.geo.addPlaneSurface([square_loop])
    transition_surfaces = [gmsh.model.geo.addPlaneSurface([loop]) for loop in transition_loops]
    geo_content += f"Plane Surface({square_surface}) = {{{square_loop}}};\n"
    
    for i, loop in enumerate(transition_loops):
        geo_content += f"Plane Surface({transition_surfaces[i]}) = {{{loop}}};\n"

    # Apply Transfinite Meshing
    #all_surfaces = [square_surface] + transition_surfaces
    all_surfaces = transition_surfaces

    for i, surface in enumerate(all_surfaces):
        gmsh.model.geo.mesh.setTransfiniteSurface(surface)
        geo_content += f"Transfinite Surface({surface});\n"

    for line in diamond_lines + arc_lines + sq_lines:
        gmsh.model.geo.mesh.setTransfiniteCurve(line, radial_elem_eigth)  # Adjust divisions as needed
        geo_content += f"Transfinite Curve{{{line}}}= {radial_elem_eigth};\n"
        
    for line in radial_lines:
        gmsh.model.geo.mesh.setTransfiniteCurve(line, radial_elem_eigth)  # Adjust divisions as needed
        geo_content += f"Transfinite Curve{{{line}}}= {radial_elem_eigth};\n"

    # Optional: Recombine surfaces to get quadrilateral elements
    for surface in all_surfaces:
        gmsh.model.geo.mesh.setRecombine(2, surface)
        geo_content += f"Recombine Surface({surface});\n"

    gmsh.model.geo.synchronize()

    gmsh.model.mesh.generate(2)


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

    # Print connectivity
    print("\nElement Connectivity (Quads):")
    for elem_type, tags, nodes in zip(element_types, element_tags, element_node_tags):
        if elem_type == 3:  # Quad elements (GMSH element type for quadrilaterals is 3)
            num_nodes_per_elem = 4  # Quads have 4 nodes
            for i, elem_tag in enumerate(tags):
                node_indices = nodes[i * num_nodes_per_elem : (i + 1) * num_nodes_per_elem]
                print(f"Quad element {elem_tag}: Nodes: {node_indices}")

    # Save mesh and geometry files
    gmsh.write("diamond_to_circle.msh")
    if export_geo:
        with open("diamond_to_circle.geo", "w") as f:
            f.write(geo_content)
 
    gmsh.finalize()

#def create_mesh(l = 0.04, lc=0.0022, r_outer=0.032, r_large=0.18, l_tot = 0.22, export_geo=True):
# Run the mesher and export .geo
r_large=0.18
create_mesh(0.1,0.005,r_large-0.085,r_large,0.22)






