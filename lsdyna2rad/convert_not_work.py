el_conn = []

class SectionHandler:
    def __init__(self, radioss_file):
        self.radioss_file = radioss_file

    def handle_line(self, line):
        pass

    def finalize(self):
        pass

#*PART
#title
#PID     SECID   MID     EOSID   HGID    GRAV    ADPFLAG

#/PART/part_ID/unit_ID
 #part_title
#prop_ID	mat_ID	subset_ID	Thick	 	

class PartHandler(SectionHandler):
    def __init__(self, radioss_file):
        super().__init__(radioss_file)
        self.lines = []

    def handle_line(self, line):
        self.lines.append(line.strip())

    def finalize(self):
        print ("parsing part")


        title = self.lines[0]
        parts = self.lines[1].split()
        secid = 0
        mid = 0
        #secid = self.lines[2].split()[0]
        #mid = self.lines[3].split()[0]
        eosid = 0
        hgid = 0
        grav = 0.0
        adpflag = 0

        self.radioss_file.write(f"/PART/{parts[0]}\n")
        self.radioss_file.write(f"{title}\n")
        #self.radioss_file.write(f"{pid} {secid} {mid} {eosid} {hgid} {grav} {adpflag}\n")
        formatted_line = (
            f"{parts[1]:>10}{parts[2]:>10}\n"
        )
        self.radioss_file.write("#prop_ID	mat_ID	subset_ID	Thick\n")
        self.radioss_file.write(formatted_line)
        

class NodeHandler:
    def __init__(self, nodes_dict):
        #super().__init__(radioss_file)
        self.nodes = nodes_dict  # ← This line is essential!
        #self.nodes = nodes_dict  # Shared dictionary: { node_id: (x, y, z) }
        #nodes_dict = {}
        
    def handle_line(self, line):
        parts = line.strip().split()
        if len(parts) >= 4:
            nid = int(parts[0])
            x, y, z = map(float, parts[1:4])
            self.nodes[nid] = (x, y, z)

    @staticmethod
    def write_nodes(radioss_file, nodes):
        radioss_file.write("/NODE\n")
        for nid, (x, y, z) in nodes.items():
            radioss_file.write(f"{nid:<10}{x:<15.6f}{y:<15.6f}{z:<15.6f}\n")

### ORIGINAL WITH NO DICT
#class ElementHandler(SectionHandler):
#    def __init__(self, radioss_file, element_type):
        super().__init__(radioss_file)
        self.element_type = element_type
        self.elements_by_part = {}  # Dictionary: part_id -> list of lines

    def handle_line(self, line):
        parts = line.split()
        if not parts:
            return

        # LS-DYNA: line[0] = elem_id, line[1:-1] = connectivity, line[-1] = part_id
        try:
            part_id = int(parts[-1])
            if part_id not in self.elements_by_part:
                self.elements_by_part[part_id] = []
            self.elements_by_part[part_id].append(parts[:-1])  # exclude the part ID
        except ValueError:
            print(f"Warning: could not parse part ID in line: {line}")

    def finalize(self):
        for part_id, elements in self.elements_by_part.items():
            self.radioss_file.write(f'/{self.element_type}/{part_id}\n')
            for parts in elements:
                if self.element_type == 'BRICK' and len(parts) >= 9:
                    line_fmt = ''.join(f"{p:<10}" for p in parts[:9]) + '\n'
                elif self.element_type == 'QUAD' and len(parts) >= 5:
                    line_fmt = ''.join(f"{p:<10}" for p in parts[:5]) + '\n'
                else:
                    continue
                self.radioss_file.write(line_fmt)
            self.radioss_file.write

class ElementHandler:
    def __init__(self, elements_dict, elem_type):
        self.elements = elements_dict 
        self.elem_type = elem_type

    def handle_line(self, line):
        parts = line.strip().split()
        if len(parts) >= 9:
            eid = int(parts[0])
            nodes = [int(p) for p in parts[1:9]]
            self.elements[eid] = nodes

    @staticmethod
    def write_elements(radioss_file, elements):
        radioss_file.write("/BRICK\n")
        for eid, conn in elements.items():
            radioss_file.write(f"{eid:<10}" + ''.join(f"{nid:<10}" for nid in conn) + "\n")
 
class ElementHandler:
    def __init__(self, elem_type):
        self.elements_by_part = {}  # Dict[int, Dict[int, List[int]]]
        self.elem_type = elem_type  # "BRICK", "QUAD", etc.

    def handle_line(self, line):
        parts = line.strip().split()
        if not parts:
            return

        try:
            eid = int(parts[0])
            nodes = [int(p) for p in parts[1:-1]]  # Exclude last (part ID)
            part_id = int(parts[-1])

            if part_id not in self.elements_by_part:
                self.elements_by_part[part_id] = {}

            self.elements_by_part[part_id][eid] = nodes

        except ValueError:
            print(f"Warning: couldn't parse line: {line}")

    def finalize(self, radioss_file):
        for part_id, elements in self.elements_by_part.items():
            radioss_file.write(f'/{self.elem_type}/{part_id}\n')
            for eid, nodes in elements.items():
                radioss_file.write(f"{eid:<10}" + ''.join(f"{nid:<10}" for nid in nodes) + "\n")
        

#*CONTACT_AUTOMATIC_NODES_TO_SURFACE_ID
#$     cid    ssid    msid     sstyp  mstyp    sboxid  mboxid  spr        mpr
#$     fs     fd      dc       vc     vdc      penchk  bt      dt         sfs
class ContactHandler(SectionHandler):
    def __init__(self, radioss_file):
        super().__init__(radioss_file)
        self.lines = []
        self.contact_id = None

    def handle_line(self, line):
        if not line.strip():
            return
        self.lines.append(line.strip())

    def finalize(self):
        if len(self.lines) < 2:
            print("Invalid contact definition, skipping...")
            return

        # Determine where CID is located
        if len(self.lines) == 4:
            self.contact_id = int(self.lines[0].split()[0])
            line1 = self.lines[1].split()
            line2 = self.lines[2].split()
            line3 = self.lines[3].split()
        elif len(self.lines) == 3:
            self.contact_id = 1  # fallback
            line1 = self.lines[0].split()
            line2 = self.lines[1].split()
            line3 = self.lines[2].split()
        else:
            self.contact_id = 1  # fallback
            line1 = self.lines[0].split()
            line2 = self.lines[1].split()
            line3 = []

        # Default values
        #MASTER IS SURFACE, SLAVE IS GRNOD
        ssid = int(line1[0]) + 100 if len(line1) > 0 else 0
        msid = int(line1[1])       if len(line1) > 1 else 0

        # Friction and optional values
        static_friction = float(line2[0]) if len(line2) > 0 else 0.0
        dynamic_friction = float(line2[1]) if len(line2) > 1 else static_friction

        # Write the /INTER/TYPE7 block
        self.radioss_file.write(f"/INTER/TYPE7/{self.contact_id}\n")
        self.radioss_file.write(f"Converted from *CONTACT_AUTOMATIC_NODES_TO_SURFACE_ID\n")
        self.radioss_file.write(f"#  Slav_id   Mast_id      Istf      Ithe      Igap                Ibag      Idel     Icurv      Iadm\n")
        self.radioss_file.write(f"{ssid:>10}{msid:>10}         0         1         0         0\n")  # ISlave, IMaster, Igap=1

        self.radioss_file.write(f"#          Fscalegap             GAP_MAX             Fpenmax\n")
        self.radioss_file.write(f"                   0                   0                   0\n")
        self.radioss_file.write(f"#              Stmin               Stmax          %mesh_size               dtmin  Irem_gap\n")
        self.radioss_file.write(f"                   0                   0                   0                   0         0\n")
        self.radioss_file.write(f"#              Stfac                Fric              Gapmin              Tstart               Tstop\n")
        self.radioss_file.write(f"                   1                  0.                  .0                   0                   0\n")
        self.radioss_file.write(f"#      IBC                        Inacti                VisS                VisF              Bumult\n")
        self.radioss_file.write(f"       000                             0                   1                   1                   0\n")
        self.radioss_file.write(f"#    Ifric    Ifiltr               Xfreq     Iform   sens_ID\n")
        self.radioss_file.write(f"         0         0                   0         0         0\n")


        self.radioss_file.write(f"#-- Kthe	          |fct_IDK  |	 	      |         Tint	    |Ithe_form| -----AscaleK ---  |\n")
        self.radioss_file.write(f"15000               0                   0                   1\n")
        self.radioss_file.write(f"#----   Frad	      |       Drad	      |       Fheats	    |    Fheatm     -----\n")
        self.radioss_file.write(f"0                   0                   0                   0\n")
        self.radioss_file.write(f"#---1----|----2----|----3----|----4----|----5----|----6----|----7----|----8----|----9----|---10----|\n")

class NodeSetHandler(SectionHandler):
    def __init__(self, radioss_file):
        super().__init__(radioss_file)
        self.set_id = 0
        self.nodes = []
        self._found_first_valid = False
        self.title_checked = False
        self._line_count = 0
        self.title = ""
                
    def handle_line(self, line):
        self._line_count += 1
        parts = line.strip().split()
        # Skip the first line (LS-DYNA keyword)
        if self._line_count == 1:
            print ("FIRST FIELD", parts[0])
            if parts and not parts[0].isdigit():
                self.title = parts[0]

                self.title_checked = True
                print("TITLE: ",self.title)
                return 
            else:
                # No ID found, fallback
                self.title_checked = True
                #NO RETURN; MAY CONTAIN SET ID

        # Skip empty or comment lines
        if not parts or parts[0].startswith('$'):
            return

        # First valid line with node data
        if not self._found_first_valid:
            if parts[0].isdigit():
                print ("FIRST FIELD NOT VALID, NEW ID", parts[0])
                self.set_id = int(parts[0])
                self._found_first_valid = True
                # Skip this first valid line
                return
            else:
                return  # Still skipping until valid data found

        # Process subsequent node lines
        self.nodes.extend(int(p) for p in parts if (p.isdigit() and int(p)>0))

    def finalize(self):
        self.radioss_file.write(f'/GRNOD/NODE/{self.set_id}\n')
        self.radioss_file.write(f'{self.title}\n')
        for i, node in enumerate(self.nodes, 1):
            self.radioss_file.write(f"{node:>10}")
            if i % 10 == 0 or i == len(self.nodes):
                self.radioss_file.write('\n')
        #self.radioss_file.write('\n')

class SectionSolidHandler(SectionHandler):
    def __init__(self, radioss_file):
        super().__init__(radioss_file)
        self.sections = []  # Store tuples: (sec_id, el_form, title)

    def handle_line(self, line):
        parts = line.strip().split()
        if not parts:
            return

        # First valid line after *SECTION_SOLID is usually:
        # sec_id   el_form   hr     title(optional)
        try:
            sec_id = int(parts[0])
            el_form = int(parts[1]) if len(parts) > 1 else 1  # Default to 1
            title = " ".join(parts[2:]) if len(parts) > 2 else "SolidSection"
            self.sections.append((sec_id, el_form, title))
        except ValueError:
            print(f"Warning: could not parse section solid line: {line}")

    def finalize(self):
        for sec_id, el_form, title in self.sections:
            self.radioss_file.write(f"/PROP/SOLID/{sec_id}\n")
            self.radioss_file.write(f"{title}\n")
            self.radioss_file.write(f"{el_form:<10}2\n\n\n")  # el_form, default density scaling

class SegmentSetHandler(SectionHandler):
    def __init__(self, radioss_file):
        super().__init__(radioss_file)
        self.title = "SEGMENT_SET"
        self.set_id = None
        self.nodes = set()
        self._line_count = 0
        self._found_id = False

    def handle_line(self, line):
        stripped = line.strip()
        if not stripped:
            return

        self._line_count += 1

        # First non-empty line: optional title
        if self._line_count == 1:
            if not stripped[0].isdigit():
                self.title = stripped
                return  # Title line, skip to next
            else:
                self._line_count += 1  # No title line, this is ID line

        # Second line: ID
        if not self._found_id:
            parts = stripped.split()
            if parts and parts[0].isdigit():
                self.set_id = int(parts[0])+100
                self._found_id = True
                print("Createg seggment set ",self.set_id )
            return

        # From third line: segment lines
        parts = stripped.split()
        segment_nodes = [int(p) for p in parts if p.isdigit()]
        self.nodes.update(segment_nodes)

    def finalize(self):
        if not self.set_id:
            self.set_id = 999999  # fallback ID if none found

        self.radioss_file.write(f"/GRNOD/NODE/{self.set_id}\n")
        self.radioss_file.write(f"$ {self.title}\n")
        node_list = sorted(self.nodes)

        for i, node in enumerate(node_list, 1):
            self.radioss_file.write(f"{node:>10}")
            if i % 10 == 0 or i == len(node_list):
                self.radioss_file.write('\n')

# OPENRADIOSS ORDERING
#      8 -------- 7
#     /|         /|
#    5 -------- 6 |
#    | |        | |
#    | 4 -------|-3
#    |/         |/
#    1 -------- 2
# LS
#   n4--------n3
#   |          |
#   |          |
#   n1--------n2      (bottom face)
#   n8--------n7
#   |          |
#   |          |
#   n5--------n6      (top face)
class SegmentSetHandlerSurf(SectionHandler):
    def __init__(self, radioss_file, element_connectivities):
        super().__init__(radioss_file)
        self.title = "SEGMENT_SET"
        self.set_id = None
        self.segments = set()  # use a set to avoid duplicate segments
        self._line_count = 0
        self._found_id = False
        self.el_conn = element_connectivities  # dict: elem_id -> [n1..n8]

    def handle_line(self, line):
        stripped = line.strip()
        if not stripped:
            return

        self._line_count += 1

        # First line is optional title
        if self._line_count == 1 and not stripped[0].isdigit():
            self.title = stripped
            return

        # Second line: set ID
        if not self._found_id:
            parts = stripped.split()
            if parts and parts[0].isdigit():
                self.set_id = int(parts[0])
                self._found_id = True
                print("Creating segment set", self.set_id)
            return

        # From third line: element IDs
        elem_ids = [int(p) for p in stripped.split() if p.isdigit()]
        # Iterate through each element ID and find its connectivity
        for eid in elem_ids:
            if eid in self.el_conn:  # Ensure the element ID is in the dictionary
                conn = self.el_conn[eid]  # Get the connectivity for the element
                # Get the faces with the correct orientation
                for face in self.get_radioss_oriented_faces(conn):
                    # Add as tuple to prevent duplicates
                    self.segments.add(tuple(face))

    def get_radioss_oriented_faces(self, conn):
        #print("CONN: ", conn)
        # conn = [n1,n2,n3,n4,n5,n6,n7,n8] from LS-DYNA
        # OpenRadioss face ordering:
        return [
            [conn[0], conn[1], conn[2], conn[3]],  # bottom
            [conn[4], conn[5], conn[6], conn[7]],  # top
            [conn[0], conn[4], conn[7], conn[3]],  # front
            [conn[1], conn[5], conn[6], conn[2]],  # right
            [conn[2], conn[6], conn[7], conn[3]],  # back
            [conn[0], conn[1], conn[5], conn[4]],  # left
        ]

    def finalize(self):
        print(f"Writing {len(self.segments)} segments")
        if not self.set_id:
            self.set_id = 999999

        self.radioss_file.write(f"/SURF/SEG/{self.set_id}\n")
        self.radioss_file.write(f"{self.title}\n")

        for i, seg in enumerate(self.segments, start=1):
            self.radioss_file.write(f"{i:<10}" + ''.join(f"{n:<10}" for n in seg) + "\n")


class BoundarySPCSetHandler(SectionHandler):
    def __init__(self, radioss_file):
        super().__init__(radioss_file)
        self.set_id = None
        self.dofs = [0, 0, 0]

    def handle_line(self, line):
        # Expecting one line with: set_id dof1 dof2 dof3 dof4 dof5 dof6
        parts = line.strip().split()
        if len(parts) >= 4:
            self.set_id = int(parts[0])
            self.dofs = [int(d) for d in parts[2:5]]
        else:
            print("Warning: Invalid *BOUNDARY_SPC_SET format.")

    def finalize(self):
        if self.set_id is None:
            return

        # Convert DOF list to a single 6-digit Trarot string
        trarot = ''.join(str(d) for d in self.dofs)

        self.radioss_file.write(f'/BCS/{self.set_id}\n')
        self.radioss_file.write(f'SPC_set_{self.set_id}\n')
        self.radioss_file.write(f'   {trarot} 111         0{self.set_id:>10}\n')  # Skew_ID = 0        

def get_mesh(line, radioss_file, nodes, elements):
    if line.startswith('*NODE'):
        return NodeHandler(nodes)
    elif line.startswith('*ELEMENT_SOLID'):
        return ElementHandler(elements,'BRICK')
    return None

#SECTION DISPATCHER
def get_handler(line, radioss_file, set_name_map,conn):
    if line.startswith('*ELEMENT_SHELL'):
        return ElementHandler(radioss_file, 'QUAD')
    elif line.startswith('*CONTACT_AUTOMATIC_NODES_TO_SURFACE_ID'):
        return ContactHandler(radioss_file)
    elif line.startswith('*SET_SEGMENT_TITLE'):
        return SegmentSetHandler(radioss_file)
        #return SegmentSetHandlerSurf(radioss_file,conn)
    elif line.startswith('*SET_NODE_LIST'):
        return NodeSetHandler(radioss_file)
    elif line.startswith('*PART'):
        return PartHandler(radioss_file)
    elif line.startswith('*SECTION_SOLID'):
        return SectionSolidHandler(radioss_file)
    elif line.startswith('*BOUNDARY_SPC_SET'):        
        return BoundarySPCSetHandler(radioss_file)
    return None

def print_header(radioss_file):
    radioss_file.write("#RADIOSS STARTER\n")
    radioss_file.write("/BEGIN\n")
    radioss_file.write("test     \n")                                                   
    radioss_file.write("      2019         0 \n")
    radioss_file.write("                  kg                   m                   s\n")
    radioss_file.write("                  kg                   m                   s   \n")  
                      

def convert_lsdyna_to_radioss(input_file, output_file):
    set_name_map = {}
    current_handler = None

    # Temporary storage for nodes and elements
    nodes = {}      # node_id: [x, y, z]
    elements = {}   # elem_id: [n1, n2, ..., n8]

    with open(input_file, 'r') as dyna_file:
        lines = dyna_file.readlines()

    # First pass: gather mesh
    current_handler = None
    for line in lines:
        line = line.strip()
        if line.startswith('$') or not line:
            continue
        if line.upper().startswith('*'):
            current_handler = get_mesh(line.upper(), None, nodes, elements)
        elif current_handler:
            current_handler.handle_line(line)
    
    print ("NODE SIZE: ", len(nodes) )
    # Now generate radioss file using the collected mesh
    with open(output_file, 'w') as radioss_file:
        print_header(radioss_file)

        # Write nodes and elements
        NodeHandler.write_nodes(radioss_file, nodes)
        ElementHandler.write_elements(radioss_file, elements)

        # Second pass: handle all other sections
        current_handler = None
        for line in lines:
            line = line.strip()
            if line.startswith('$') or not line:
                continue
            line_up = line.upper()

            if line_up.startswith('*NODE') or line_up.startswith('*ELEMENT_SOLID'):
                continue  # Skip, already handled

            if line_up.startswith('*'):
                if current_handler:
                    current_handler.finalize()
                current_handler = get_handler(line_up, radioss_file, set_name_map,elements)
            elif current_handler:
                current_handler.handle_line(line)

        if current_handler:
            current_handler.finalize()

        radioss_file.write('/END\n')

    print(f"Conversion complete! Radioss file saved to: {output_file}")

# =============================================
# Usage Example
# =============================================
input_k_file = "corte_2.k"        # Input LS-DYNA file
output_rad_file = "model_0000.rad"  # Output Radioss file

convert_lsdyna_to_radioss(input_k_file, output_rad_file)
#print (el_conn)
