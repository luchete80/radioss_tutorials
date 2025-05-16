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
        

class NodeHandler(SectionHandler):
    def __init__(self, radioss_file):
        super().__init__(radioss_file)
        self.radioss_file.write('/NODE\n')

    def handle_line(self, line):
        parts = line.split()
        if len(parts) >= 4:
            formatted_line = (
                f"{parts[0]:>10}{parts[1]:>20}{parts[2]:>20}{parts[3]:>20}\n"
            )
            self.radioss_file.write(formatted_line)

### ORIGINAL WITH NO DICT
class ElementHandler(SectionHandler):
    def __init__(self, radioss_file, element_type):
        super().__init__(radioss_file)
        self.element_type = element_type
        self.elements_by_part = {}  # Dictionary: part_id -> list of lines

    def handle_line(self, line):
        parts = line.split()
        if not parts:
            return

        # LS-DYNA: line[0] = elem_id, line[1:-1] = connectivity, line[-1] = part_id
        try:
            part_id = int(parts[1])
            if part_id not in self.elements_by_part:
                self.elements_by_part[part_id] = []
            self.elements_by_part[part_id].append(parts)  # exclude the part ID
        except ValueError:
            print(f"Warning: could not parse part ID in line: {line}")

    def finalize(self):
        for part_id, elements in self.elements_by_part.items():
            self.radioss_file.write(f'/{self.element_type}/{part_id}\n')
            for parts in elements:
                if self.element_type == 'BRICK' and len(parts) >= 9:
                    line_fmt = f"{parts[0]:<10}"  + ''.join(f"{p:<10}" for p in parts[2:10]) + '\n'
                elif self.element_type == 'QUAD' and len(parts) >= 5:
                    line_fmt = ''.join(f"{p:<10}" for p in parts[:5]) + '\n'
                else:
                    continue
                self.radioss_file.write(line_fmt)
            self.radioss_file.write


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
                print("Createg Node set from segment, id 100 + ",self.set_id )
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

class PrescribedMotionSetHandler(SectionHandler):
    def __init__(self, radioss_file):
        super().__init__(radioss_file)
        self.set_id = None
        self.dof = None
        self.velocity = None
        self.funct       = None
        self.skew_id = 0  # default no skew
        self.title = ""
        self.line_count = 0

    def handle_line(self, line):
        stripped = line.strip()
        if not stripped:
            return

        self.line_count += 1
        
        print ("Parts", stripped, "line ", self.line_count)
        #if self.line_count == 1 and not stripped.startswith("*"):
        #    self.title = stripped
        #    return

        parts = stripped.split()
        

        # Example LS-DYNA line: set_id dof vel
        if len(parts) >= 4:
            self.set_id = int(parts[0])
            self.dof = int(parts[1])
            self.velocity = int(parts[2])
            self.funct = int(parts[3])
        else:
            print(f"Warning: Invalid *PRESCRIBED_MOTION_SET format in line: {line}")

    def finalize(self):
        if self.set_id is None or self.dof is None :
            print("Warning: Incomplete prescribed motion data.")
            return

        #*BOUNDARY_PRESCRIBED_MOTION_SET
        #set_id DOF VAD LCID SCALFAC

        self.radioss_file.write(f"/IMPVEL/1\n")
        self.radioss_file.write(f"{self.title or f'ImpVel_{self.set_id}'}\n")
        self.radioss_file.write(f"#funct_IDT       Dir   skew_ID sensor_ID  grnod_ID  frame_ID     Icoor\n")
        if (self.dof == 1):
          dir_ = "X"
        elif (self.dof == 2):
          dir_ = "Y"
        elif (self.dof == 2):
          dir_ = "Z"
        self.radioss_file.write(f"{self.funct:>10}{dir_:>10}{self.velocity:>10}"+"         0" +f"{self.set_id:>10}" + "         0         0"+ "\n")
        self.radioss_file.write(f"#           Ascale_x            Fscale_Y              Tstart               Tstop\n")
        self.radioss_file.write(f"                   0                   1                   0               11000\n")
        #           0                  -1                   0               11000
# SECTION DISPATCHER
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
        return SegmentSetHandler(radioss_file)
    elif line.startswith('*SET_NODE_LIST'):
        return NodeSetHandler(radioss_file)
    elif line.startswith('*PART'):
        return PartHandler(radioss_file)
    elif line.startswith('*SECTION_SOLID'):
        return SectionSolidHandler(radioss_file)
    elif line.startswith('*BOUNDARY_SPC_SET'):
        return BoundarySPCSetHandler(radioss_file)
    elif line.startswith('*BOUNDARY_PRESCRIBED_MOTION_SET'):        
        return PrescribedMotionSetHandler(radioss_file)
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

    with open(input_file, 'r') as dyna_file, open(output_file, 'w') as radioss_file:
        print_header(radioss_file)
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
    
        radioss_file.write('/END\n')
    print(f"Conversion complete! Radioss file saved to: {output_file}")

# =============================================
# Usage Example
# =============================================
input_k_file = "corte_2.k"        # Input LS-DYNA file
output_rad_file = "model_0000.rad"  # Output Radioss file

convert_lsdyna_to_radioss(input_k_file, output_rad_file)
#print (el_conn)
