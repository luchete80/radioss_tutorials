
mat_Ajc  = 359.0e6
mat_Bjc   = 327.0e6
mat_njc   = 0.454
mat_mjc   = 0.919
mat_Cjc   = 0.0786
mat_e0jc  = 0.04


# Open the VTK file and read all lines
filename = "Robot CNC M2 45.vtk"  # Replace with your actual file path
new_filename = "modified_" + filename  # Output file



with open(filename, 'r') as file:
    lines = file.readlines()

# Find the starting line of the target element field
field_name = "2DELEM_Plastic_Strain_Upper"
start_idx = None

for i, line in enumerate(lines):
    if field_name in line:
        start_idx = i
        break

if start_idx is None:
    raise ValueError(f"Field '{field_name}' not found in the file.")

# Parse the header to determine components
header_line = lines[start_idx].strip().split()
num_components = int(header_line[-1]) if header_line[-1].isdigit() else 1

# Skip the LOOKUP_TABLE line if present
lookup_idx = start_idx + 1
if "LOOKUP_TABLE" in lines[lookup_idx]:
    data_start_idx = lookup_idx + 1
else:
    data_start_idx = lookup_idx

# Read the data until the next section
plastic_strain_upper = []
data_end_idx = data_start_idx  # Track where data ends
for i, line in enumerate(lines[data_start_idx:], start=data_start_idx):
    line = line.strip()
    if line.startswith(("CELL_DATA", "POINT_DATA", "SCALARS", "VECTORS", "TENSORS")):
        data_end_idx = i
        break
    plastic_strain_upper.extend(map(float, line.split()))

# Handle the case where data extends to the end of the file
if data_end_idx == data_start_idx:
    data_end_idx = len(lines)
    
    
###############################################

# Find the starting line of the target element field
field_name_s = "TENSORS 2DELEM_Stress_(upper)"
start_idx_s = None

for i, line in enumerate(lines):
    if field_name_s in line:
        start_idx_s = i
        break

if start_idx_s is None:
    raise ValueError(f"Field '{field_name}' not found in the file.")

# Parse the header to determine components
header_line = lines[start_idx_s].strip().split()
num_components = int(header_line[-1]) if header_line[-1].isdigit() else 1

# Skip the LOOKUP_TABLE line if present
lookup_idx = start_idx_s + 1
if "LOOKUP_TABLE" in lines[lookup_idx]:
    data_start_idx_s = lookup_idx + 1
else:
    data_start_idx_s = lookup_idx

# Read the data until the next section
stress_upper = []
data_end_idx_s = data_start_idx_s  # Track where data ends
for i, line in enumerate(lines[data_start_idx_s:], start=data_start_idx_s):
    line = line.strip()
    if line.startswith(("CELL_DATA", "POINT_DATA", "SCALARS", "VECTORS", "TENSORS")):
        data_end_idx_s = i
        break
    stress_upper.extend(map(float, line.split()))

print ("Stress field length (x6)",len( stress_upper),"x1 ",len( stress_upper)/9)

# Handle the case where data extends to the end of the file
if data_end_idx_s == data_start_idx_s:
    data_end_idx_s = len(lines)
    
###################################################
print(stress_upper)
# Perform the operation: 1 + field value
modified_field = [(mat_Ajc + mat_Bjc * pow(value,mat_njc))*(1+mat_Cjc) for value in plastic_strain_upper]
#modified_field = [(mat_Ajc + mat_Bjc * pow(value,mat_njc))*(1+mat_Cjc)/val2 for value, val2 in zip(plastic_strain_upper, stress_upper)]

# Format the new field
new_field_name = "End_Upper_Yield_Stress"
new_field_header = f"SCALARS {new_field_name} float {num_components}\nLOOKUP_TABLE default\n"

# Format data into lines (e.g., 5 values per line)
new_field_data = ""
for i in range(0, len(modified_field), 5):
    line_values = modified_field[i:i + 5]
    new_field_data += " ".join(f"{val:.6f}" for val in line_values) + "\n"

# Insert the new field after the original data
new_lines = lines[:data_end_idx] + [new_field_header, new_field_data] + lines[data_end_idx:]

# Write the modified VTK file
with open(new_filename, 'w') as file:
    file.writelines(new_lines)

print(f"New field '{new_field_name}' added and saved as '{new_filename}'.")
