# =============================================
# LS-DYNA to Radioss Node/Element Converter
# Converts *NODE and *ELEMENT_SOLID/*ELEMENT_SHELL to Radioss format
# Uses fixed-width field formatting in output
# =============================================

def convert_lsdyna_to_radioss(input_file, output_file):
    with open(input_file, 'r') as dyna_file, open(output_file, 'w') as radioss_file:
        in_nodes = False
        in_elements = False
        element_type = None
        
        # Field widths configuration
        node_id_width = 10
        coord_width = 20
        elem_id_width = 10
        node_ref_width = 10
        
        for line in dyna_file:
            line = line.strip().upper()
            
            # Detect *NODE section
            if line.startswith('*NODE'):
                in_nodes = True
                radioss_file.write('/NODE/1\n')  # Radioss node format
                continue
            
            # Detect *ELEMENT_SOLID or *ELEMENT_SHELL
            elif line.startswith('*ELEMENT_SOLID'):
                in_elements = True
                element_type = 'BRICK'
                radioss_file.write(f'/ELEMENT/{element_type}/1\n')
                continue
            elif line.startswith('*ELEMENT_SHELL'):
                in_elements = True
                element_type = 'QUAD'  # or 'TRIA' for triangles
                radioss_file.write(f'/ELEMENT/{element_type}/1\n')
                continue
            
            # End of section
            elif line.startswith('*') and ('NODE' in line or 'ELEMENT' in line):
                in_nodes = False
                in_elements = False
            
            # Process node data with fixed-width fields
            if in_nodes and line and not line.startswith('*'):
                parts = line.split()
                if len(parts) >= 4:
                    node_id = parts[0].strip()
                    x = parts[1].strip()
                    y = parts[2].strip()
                    z = parts[3].strip()
                    
                    # Format with fixed width
                    formatted_line = (f"{node_id:>{node_id_width}}"
                                     f"{x:>{coord_width}}"
                                     f"{y:>{coord_width}}"
                                     f"{z:>{coord_width}}\n")
                    radioss_file.write(formatted_line)
            
            # Process element data with fixed-width fields
            elif in_elements and line and not line.startswith('*'):
                parts = [p.strip() for p in line.split() if p.strip()]
                
                if element_type == 'BRICK' and len(parts) >= 9:
                    # Solid element (8 nodes)
                    formatted_line = (f"{parts[0]:<{elem_id_width}}"
                                     f"{parts[1]:<{node_ref_width}}"
                                     f"{parts[2]:<{node_ref_width}}"
                                     f"{parts[3]:<{node_ref_width}}"
                                     f"{parts[4]:<{node_ref_width}}"
                                     f"{parts[5]:<{node_ref_width}}"
                                     f"{parts[6]:<{node_ref_width}}"
                                     f"{parts[7]:<{node_ref_width}}"
                                     f"{parts[8]:<{node_ref_width}}\n")
                    radioss_file.write(formatted_line)
                    
                elif element_type == 'QUAD' and len(parts) >= 5:
                    # Shell element (4 nodes)
                    formatted_line = (f"{parts[0]:<{elem_id_width}}"
                                    f"{parts[1]:<{node_ref_width}}"
                                    f"{parts[2]:<{node_ref_width}}"
                                    f"{parts[3]:<{node_ref_width}}"
                                    f"{parts[4]:<{node_ref_width}}\n")
                    radioss_file.write(formatted_line)

        print(f"Conversion complete! Radioss file saved to: {output_file}")




def convert_contact_to_inter(input_file, output_file):
    with open(input_file, 'r') as dyna_file, open(output_file, 'w') as radioss_file:
        in_contact = False
        contact_data = []
        
        # Fixed field widths for Radioss output
        field_widths = {
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
            
            # Detect CONTACT section
            if line.startswith('*CONTACT_AUTOMATIC_NODES_TO_SURFACE_ID'):
                in_contact = True
                continue
            
            # End of section
            elif line.startswith('*') and in_contact:
                in_contact = False
                break  # Assuming we only process the first contact found
            
            # Process contact data
            if in_contact and line and not line.startswith('$'):
                # Skip comment lines
                if line.startswith('$'):
                    continue
                
                # Parse contact card (assuming fixed format or space-separated)
                parts = line.split()
                if len(parts) >= 8:
                    contact_data = {
                        'id': parts[0],
                        'ssid': parts[1],  # Slave node set ID
                        'msid': parts[2],  # Master segment set ID
                        'fric': parts[7] if len(parts) > 7 else '0.0'  # Friction coefficient
                    }
        
        # Write Radioss INTER/TYPE7 entry if contact data was found
        if contact_data:
            # Write header
            radioss_file.write('/INTER/TYPE7\n')
            
            # Format and write main card
            main_card = (
                f"{contact_data['id']:<{field_widths['id']}}"
                #f"7{:<{field_widths['type']}}"  # TYPE7
                f"{contact_data['msid']:<{field_widths['main']}}"  # Main surface
                f"{contact_data['ssid']:<{field_widths['secondary']}}"  # Secondary surface
                f"{contact_data['fric']:<{field_widths['fric']}}"  # Friction
                f"{0:<{field_widths['igstyp']}}"  # IGSTYP (default 0)
                f"{0:<{field_widths['ibsort']}}"  # IBSORT (default 0)
                f"{1:<{field_widths['ifric']}}"  # IFRIC (1=friction active)
                f"{0:<{field_widths['i2sort']}}"  # I2SORT (default 0)
                f"\n"
            )
            radioss_file.write(main_card)
            
            # Write optional cards (default values)
            radioss_file.write(
                f"{'':<{field_widths['id']}}"  # Empty first field
                f"{0.0:<{field_widths['type']}}"  # FRIC_MIN (default 0.0)
                f"{0.0:<{field_widths['main']}}"  # XFILTR (default 0.0)
                f"{0:<{field_widths['secondary']}}"  # IFLAG (default 0)
                f"{0:<{field_widths['fric']}}"  # IORTH (default 0)
                f"{0:<{field_widths['igstyp']}}"  # IEDGE (default 0)
                f"\n"
            )
            
            print(f"Conversion complete! Radioss INTER/TYPE7 saved to: {output_file}")
        else:
            print("No CONTACT_AUTOMATIC_NODES_TO_SURFACE_ID found in input file.")

# =============================================
# Usage Example
# =============================================
input_k_file = "corte_2.k"   # Your LS-DYNA input file
output_rad_file = "contact_inter.rad"  # Output Radioss file

convert_contact_to_inter(input_k_file, output_rad_file)

# =============================================
# Usage Example
# =============================================
input_k_file = "corte_2.k"   # Your LS-DYNA input file
output_rad_file = "radioss_model.rad"  # Output Radioss file

convert_lsdyna_to_radioss(input_k_file, output_rad_file)
