import numpy as np
import os

ini_node = 0
end_node = 9999
node_count = 0 


start_index = 5
end_index = 7 

T0 = 20.0
thck = 5.0e-4
L = 0.1
dens = 4430.0
c_p = 520.0

m_nod = thck * L * L * dens / (end_node-ini_node+1)

def find_integer_substring_indices(string):
    start_index = None
    end_index = None

    for i in range(len(string)):
        if string[i].isdigit():  # If the character is a digit
            if start_index is None:  # If this is the first digit encountered
                start_index = i
            end_index = i  # Update end_index on each iteration as long as digit characters are consecutive
        elif start_index is not None:  # If the consecutive digit sequence ends
            break

    return start_index

def find_integer_substring_end_indices(string):
    end_index = None

    for i in range(len(string)):
        j = len(string)-1-i
        if string[j].isdigit():  # If the character is a digit
            if end_index is None:  # If this is the first digit encountered
                end_index = j
            # print ("END DIG " + string[j])
        elif end_index is not None:  # If the consecutive digit sequence ends
            break

    return end_index
    
def convert_substring_to_integer(string, start_index, end_index):
    # Extract the substring
    # print("STRING %s" %string)
    substring = string[start_index:end_index+1]
    #print("SUBS -%s-" %substring)
    # # Convert the substring to an integer
    try:
        integer_value = int(substring)
        #print ("int %d" %integer_value)
        return integer_value
    except ValueError:
        print("Error: The substring cannot be converted to an integer.")
        return None

def write_list(force):
  fi_x = open("temp.csv","w")
  fi_x.write("t,f\n")

  dt = 1.0
  t = 0.0
  for i in range(len(force)):
    fi_x.write(str(t) + ", " + str(force [i]) + "\n" )
    print(force [i])
    t +=dt



def open_files_with_extension(directory, extension):
    # Check if the directory exists
    if not os.path.isdir(directory):
        print(f"Directory '{directory}' does not exist.")
        return
    
    # Get a list of files with the specified extension
    files = [f for f in os.listdir(directory) if f.endswith(extension)]
    
    if not files:
        print(f"No files found with '{extension}' extension in '{directory}'.")
        return
    
    
    print("Found %d files " %len(files))
    force = []
    force = np.zeros(len(files)+1)#index begins with 1

    
    first = True 
    # Open each file
    tot = len(files)
    j = 1
    for file_name in files:
      start_idx = find_integer_substring_indices(file_name)
      end_idx = find_integer_substring_end_indices(file_name)
      # print("start: " + str(start_idx) + ", end " + str(end_idx))
      file_path = os.path.join(directory, file_name)

      try:
          with open(file_path, 'r') as f:
            print("File " + file_name + " found")
            idx = convert_substring_to_integer(file_name,start_idx,end_idx)
            # print ("idx %d" %idx) 
            lines = f.readlines()
            print ("file " + str(j) + "/"+ str(tot))
            if (first):  
              for i in range (len(lines)) :
                #if (lines[i].find("VECTORS Sect.RBY,Wall_F. float") != -1):
                if (lines[i].find("SCALARS Nodal_Temperature float 1") != -1):
                  print("FOUND STRING. in line ", i, lines[i])
                  end = False    
                  i = i+2
                  line_ini = i
                  
                  while (not end):
                  #FIND NEXT OCCURRENCE
                    j = lines[i].find("VECTORS")
                    if (j != -1):
                      print("found next VECTORS in line %d",i)
                      # print (lines[j-2])
                      lf = i - 2
                      end = True
                    # print (i)
                    i +=1
              node_count = lf - line_ini -1
              print("Node Coount ", lf - line_ini + 1)
              first = False
            # print (lines[lf])
            #numbers_array = [float(num) for num in lines[lf].split()]
            
            #print ("LINE_INI: ", line_ini)
            force_z = 0.0
            force_tool_z = 0.0
            for k in range (node_count) :
              #narr = [float(num) for num in lines[line_ini+k].split()]
              #print (k+line_ini)
              #print ("LINE VAL: "+lines[line_ini+k]+"\n")
              #print ("K",k, "line", line_ini+k)
              if ( k > ini_node and k <end_node):
                #print ("energy:",m_nod * c_p * (float(lines[line_ini+k]) - T0 ))
                force_tool_z += m_nod * c_p * (float(lines[line_ini+k]) - T0)
              force_z += float(lines[line_ini+k])
            #print("WRITING FORCE in idx", idx ,", vector size: ", len(force))
            force[idx] = force_tool_z
            print ("Contact Force Sum: ", force_z, ", Contact Force in tool Node Range: ", force_tool_z)
            #print ("Contact Force", numbers_array[0], numbers_array[1],numbers_array[2])
            #force.append(numbers_array[2])
            #force[idx] =  numbers_array[2]
            j += 1
      except Exception as e:
          print(f"Error opening {file_name}: {e}")
    return force

def read_vtk_nodal_temperature(file_path, N):
    temperatures = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Locate the SCALARS field
    for i, line in enumerate(lines):
        if line.strip() == "SCALARS Nodal_Temperature float 1":
            data_start = i + 2  # Skip the LOOKUP_TABLE line
            break
    else:
        raise ValueError("Field 'Nodal_Temperature' not found in VTK file.")
    
    # Read first N temperature values
    for i in range(N):
        if data_start + i < len(lines):
            temperatures.append(float(lines[data_start + i].strip()))
    
    return temperatures

directory = '.'
extension = '.vtk'  # Change this to the extension you want to search for

# Example usage
if __name__ == "__main__":
    file_path = "test.vtk"  # Change this to your VTK file
    N = 100  # Number of nodes to read
    #temperatures = read_vtk_nodal_temperature(file_path, N)
    
    test = open_files_with_extension(directory, extension)
    #print("First", N, "nodal temperatures:", temperatures)
    write_list(test)
