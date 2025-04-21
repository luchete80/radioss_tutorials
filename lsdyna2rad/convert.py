class SectionHandler:
    def __init__(self, radioss_file):
        self.radioss_file = radioss_file

    def handle_line(self, line):
        pass

    def finalize(self):
        pass


class NodeHandler(SectionHandler):
    def __init__(self, radioss_file):
        super().__init__(radioss_file)
        self.radioss_file.write('/NODE/1\n')

    def handle_line(self, line):
        parts = line.split()
        if len(parts) >= 4:
            formatted_line = (
                f"{parts[0]:>10}{parts[1]:>20}{parts[2]:>20}{parts[3]:>20}\n"
            )
            self.radioss_file.write(formatted_line)

class ElementHandler(SectionHandler):
    def __init__(self, radioss_file, element_type):
        super().__init__(radioss_file)
        self.element_type = element_type
        self.radioss_file.write(f'/ELEMENT/{element_type}/1\n')

    def handle_line(self, line):
        parts = line.split()
        if self.element_type == 'BRICK' and len(parts) >= 9:
            line_fmt = ''.join([f"{p:<10}" for p in parts[:9]]) + '\n'
        elif self.element_type == 'QUAD' and len(parts) >= 5:
            line_fmt = ''.join([f"{p:<10}" for p in parts[:5]]) + '\n'
        else:
            return
        self.radioss_file.write(line_fmt)

class ContactHandler(SectionHandler):
    def __init__(self, radioss_file):
        super().__init__(radioss_file)
        self.data = {}

    def handle_line(self, line):
        parts = line.split()
        if len(parts) >= 8:
            self.data = {
                'id': parts[0],
                'ssid': parts[1],
                'msid': parts[2],
                'fric': parts[7] if len(parts) > 7 else '0.0'
            }

    def finalize(self):
        # Same logic from your write_contact() helper
        self.radioss_file.write('/INTER/TYPE7\n')
        w = 10
        self.radioss_file.write(
            f"{self.data['id']:<{w}}{7:<{w}}{self.data['msid']:<{w}}"
            f"{self.data['ssid']:<{w}}{self.data['fric']:<{w}}"
            f"{0:<{w}}{0:<{w}}{1:<{w}}{0:<{w}}\n"
        )
        self.radioss_file.write(f"{'':<{w}}{0.0:<{w}}{0.0:<{w}}{0:<{w}}{0:<{w}}{0:<{w}}\n")

class NodeSetHandler(SectionHandler):
    def __init__(self, radioss_file, set_id, set_name):
        super().__init__(radioss_file)
        self.set_id = set_id
        self.set_name = set_name
        self.nodes = []

    def handle_line(self, line):
        # Use space splitting instead of commas
        parts = [p.strip() for p in line.split() if p.strip()]
        self.nodes.extend(p for p in parts if p.isdigit())

    def finalize(self):
        self.radioss_file.write(f'/GRNOD/{self.set_id}\n$ {self.set_name}\n')
        for i, node in enumerate(self.nodes, 1):
            self.radioss_file.write(f"{node:>10}")
            if i % 10 == 0 or i == len(self.nodes):
                self.radioss_file.write('\n')
        self.radioss_file.write('\n')


#SECTION DISPATCHER
def get_handler(line, radioss_file, set_name_map):
    if line.startswith('*NODE'):
        return NodeHandler(radioss_file)
    elif line.startswith('*ELEMENT_SOLID'):
        return ElementHandler(radioss_file, 'BRICK')
    elif line.startswith('*ELEMENT_SHELL'):
        return ElementHandler(radioss_file, 'QUAD')
    elif line.startswith('*CONTACT_AUTOMATIC_NODES_TO_SURFACE_ID'):
        return ContactHandler(radioss_file)
    elif line.startswith('*SET_SEGMENT_TITLE'):
        parts = line.split(',')
        set_id = parts[0].split()[-1]
        set_name = parts[1].strip().strip('"\'') if len(parts) > 1 else f"Set_{set_id}"
        set_name_map[set_id] = set_name
        return None
    elif line.startswith('*SET_NODE_LIST'):
        set_id = line.split()[-1]
        return NodeSetHandler(radioss_file, set_id, set_name_map.get(set_id, f"Set_{set_id}"))
    return None

def convert_lsdyna_to_radioss(input_file, output_file):
    set_name_map = {}
    current_handler = None

    with open(input_file, 'r') as dyna_file, open(output_file, 'w') as radioss_file:
        for line in dyna_file:
            line = line.strip()
            if line.startswith('$') or not line:
                continue
            line_up = line.upper()

            if line_up.startswith('*'):
                if current_handler:
                    current_handler.finalize()
                current_handler = get_handler(line_up, radioss_file, set_name_map)
            elif current_handler:
                current_handler.handle_line(line)

        if current_handler:
            current_handler.finalize()

    print(f"Conversion complete! Radioss file saved to: {output_file}")

# =============================================
# Usage Example
# =============================================
input_k_file = "corte_2.k"        # Input LS-DYNA file
output_rad_file = "model.rad"  # Output Radioss file

convert_lsdyna_to_radioss(input_k_file, output_rad_file)
