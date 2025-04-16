# =============================================
# LS-DYNA to Radioss Full Converter
# Handles:
# - Nodes (*NODE)
# - Elements (*ELEMENT_SOLID, *ELEMENT_SHELL)
# - Contacts (*CONTACT_AUTOMATIC_NODES_TO_SURFACE_ID)
# - Node Sets (SET_SEGMENT_TITLE to GRNOD)
# =============================================

def convert_lsdyna_to_radioss(input_file, output_file):
    with open(input_file, 'r') as dyna_file, open(output_file, 'w') as radioss_file:
        # State tracking variables
        in_nodes = False
        in_elements = False
        in_contact = False
        in_node_set = False
        element_type = None
        contact_data = []
        current_set = None
        set_nodes = []
        set_name_map = {}  # Maps set IDs to names
        
        # Field width configurations
        node_id_width = 10
        coord_width = 20
        elem_id_width = 10
        node_ref_width = 10
        grnod_id_width = 10
        grnod_node_width = 10
        
        inter_widths = {
            'id': 10,
            'type': 10,
            'main': 10,
            'secondary': 10,
            'fric': 10,
            'igstyp': 10,
            'ibsort': 10,
            'ifric': 10,
            'i2sort': 10
        }
        
        for line in dyna_file:
            line = line.strip().upper()
            
            # Skip comment lines
            if line.startswith('$'):
                continue
                
            # ===== SECTION DETECTION =====
            # Detect *NODE section
            if line.startswith('*NODE'):
                in_nodes = True
                in_elements = False
                in_contact = False
                in_node_set = False
                radioss_file.write('/NODE/1\n')
                continue
            
            # Detect *ELEMENT_SOLID or *ELEMENT_SHELL
            elif line.startswith('*ELEMENT_SOLID'):
                in_elements = True
                in_nodes = False
                in_contact = False
                in_node_set = False
                element_type = 'BRICK'
                radioss_file.write(f'/ELEMENT/{element_type}/1\n')
                continue
                
            elif line.startswith('*ELEMENT_SHELL'):
                in_elements = True
                in_nodes = False
                in_contact = False
                in_node_set = False
                element_type = 'QUAD'
                radioss_file.write(f'/ELEMENT/{element_type}/1\n')
                continue
                
            # Detect CONTACT section
            elif line.startswith('*CONTACT_AUTOMATIC_NODES_TO_SURFACE_ID'):
                in_contact = True
                in_nodes = False
                in_elements = False
                in_node_set = False
                continue
                
            # Detect SET_SEGMENT_TITLE (node sets)
            elif line.startswith('*SET_SEGMENT_TITLE'):
                in_node_set = True
                in_nodes = False
                in_elements = False
                in_contact = False
                parts = line.split(',')
                if len(parts) >= 2:
                    set_id = parts[0].split()[-1].strip()
                    set_name = parts[1].strip().strip('"\'')
                    set_name_map[set_id] = set_name
                continue
                
            # Detect SET_NODE_LIST (actual node IDs)
            elif line.startswith('*SET_NODE_LIST'):
                if current_set is not None and set_nodes:
                    # Write the previous set if we have one
                    write_grnod(radioss_file, current_set, set_nodes, 
                               grnod_id_width, grnod_node_width, set_name_map)
                
                current_set = line.split()[-1].strip()  # Get set ID
                set_nodes = []
                in_node_set = True
                continue
                
            # End of any section
            elif line.startswith('*'):
                if in_contact and contact_data:
                    write_contact(radioss_file, contact_data, inter_widths)
                    contact_data = []
                
                in_nodes = False
                in_elements = False
                in_contact = False
                in_node_set = False
                
            # ===== DATA PROCESSING =====
            # Process node data
            elif in_nodes and line:
                parts = line.split()
                if len(parts) >= 4:
                    formatted_line = (
                        f"{parts[0]:>{node_id_width}}"
                        f"{parts[1]:>{coord_width}}"
                        f"{parts[2]:>{coord_width}}"
                        f"{parts[3]:>{coord_width}}\n"
                    )
                    radioss_file.write(formatted_line)
            
            # Process element data
            elif in_elements and line:
                parts = [p.strip() for p in line.split() if p.strip()]
                
                if element_type == 'BRICK' and len(parts) >= 9:
                    formatted_line = (
                        f"{parts[0]:<{elem_id_width}}"
                        f"{parts[1]:<{node_ref_width}}"
                        f"{parts[2]:<{node_ref_width}}"
                        f"{parts[3]:<{node_ref_width}}"
                        f"{parts[4]:<{node_ref_width}}"
                        f"{parts[5]:<{node_ref_width}}"
                        f"{parts[6]:<{node_ref_width}}"
                        f"{parts[7]:<{node_ref_width}}"
                        f"{parts[8]:<{node_ref_width}}\n"
                    )
                    radioss_file.write(formatted_line)
                    
                elif element_type == 'QUAD' and len(parts) >= 5:
                    formatted_line = (
                        f"{parts[0]:<{elem_id_width}}"
                        f"{parts[1]:<{node_ref_width}}"
                        f"{parts[2]:<{node_ref_width}}"
                        f"{parts[3]:<{node_ref_width}}"
                        f"{parts[4]:<{node_ref_width}}\n"
                    )
                    radioss_file.write(formatted_line)
            
            # Process contact data
            elif in_contact and line and not contact_data:
                parts = line.split()
                if len(parts) >= 8:
                    contact_data = {
                        'id': parts[0],
                        'ssid': parts[1],  # Slave nodes
                        'msid': parts[2],  # Master surface
                        'fric': parts[7] if len(parts) > 7 else '0.0'
                    }
            
            # Process node set data
            elif in_node_set and line:
                parts = [p.strip() for p in line.split(',') if p.strip()]
                for part in parts:
                    if part.isdigit():  # Only add if it's a node number
                        set_nodes.append(part)
        
        # Write any remaining sets after file processing is complete
        if current_set is not None and set_nodes:
            write_grnod(radioss_file, current_set, set_nodes, 
                       grnod_id_width, grnod_node_width, set_name_map)

        print(f"Conversion complete! Radioss file saved to: {output_file}")

def write_contact(radioss_file, contact_data, widths):
    """Helper function to write contact data in Radioss format"""
    radioss_file.write('/INTER/TYPE7\n')
    main_card = (
        f"{contact_data['id']:<{widths['id']}}"
        f"7{:<{widths['type']}}"  # TYPE7
        f"{contact_data['msid']:<{widths['main']}}"
        f"{contact_data['ssid']:<{widths['secondary']}}"
        f"{contact_data['fric']:<{widths['fric']}}"
        f"0{:<{widths['igstyp']}}"
        f"0{:<{widths['ibsort']}}"
        f"1{:<{widths['ifric']}}"
        f"0{:<{widths['i2sort']}}"
        f"\n"
    )
    radioss_file.write(main_card)
    
    # Write optional cards
    radioss_file.write(
        f"{'':<{widths['id']}}"
        f"0.0{:<{widths['type']}}"
        f"0.0{:<{widths['main']}}"
        f"0{:<{widths['secondary']}}"
        f"0{:<{widths['fric']}}"
        f"0{:<{widths['igstyp']}}"
        f"\n"
    )

def write_grnod(radioss_file, set_id, nodes, id_width, node_width, name_map):
    """Helper function to write GRNOD data in Radioss format"""
    # Write header with optional title
    title = name_map.get(set_id, f"Set_{set_id}")
    radioss_file.write(f'/GRNOD/{set_id}\n')
    radioss_file.write(f'$ {title}\n')
    
    # Write nodes (10 per line)
    line = ""
    for i, node in enumerate(nodes, 1):
        line += f"{node:>{node_width}}"
        if i % 10 == 0 or i == len(nodes):
            radioss_file.write(line + '\n')
            line = ""
    
    radioss_file.write('\n')  # Extra newline for separation

# =============================================
# Usage Example
# =============================================
input_k_file = "model.k"        # Input LS-DYNA file
output_rad_file = "model.rad"  # Output Radioss file

convert_lsdyna_to_radioss(input_k_file, output_rad_file)
