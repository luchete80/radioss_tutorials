import numpy as np
import os
import re 
import math

ini_node = 0
end_node = 63000
node_count = 0 

ini_node_f = 63000
end_node_f = 69950


tool_rad    = 2.5e-3
sphere_divs = 24

tool_elem = sphere_divs * sphere_divs * 6
print ("Tool elem")

h_tool= 325000.0

node_area = 4.0 * math.pi * tool_rad * tool_rad 


node_ball = (end_node_f - ini_node_f+1)/2
end_node_top_f = ini_node_f + node_ball


start_index = 5
end_index = 7 

T0 = 20.0
thck = 5.0e-4
L = 0.1
dens = 4430.0
c_p = 520.0

m_nod = thck * L * L * dens / (end_node-ini_node+1)

def extract_number_from_filename(filename):
    match = re.search(r'\d+', filename)  # busca la primera secuencia de dígitos
    if match:
        return int(match.group())
    return None


def write_list(heat, cold, atop, abot, cheat):
  fi_x = open("energy.csv","w")
  fi_x.write("t,heat,cold,area_top,area_bot\n")

  dt = 1.0
  t = 0.0
  for i in range(len(heat)-1):
    fi_x.write(str(t) + ", " + str(heat [i]) + ", " + str(cold [i])+ ", " + str(atop [i])+ ", " + str(abot [i]) + "\n" )
    print(heat [i])
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
    
    temperatures = {}
    area_top     = [0.0]* np.zeros(len(files)+1)#
    area_bot     = [0.0]* np.zeros(len(files)+1)#
    cont_heat    = [0.0]* np.zeros(len(files)+1)#
    

        
    first = True 
    # Open each file
    tot = len(files)
    j = 1
    for file_name in files:
      cont_heat_sum = 0.0
    
      # print("start: " + str(start_idx) + ", end " + str(end_idx))
      file_path = os.path.join(directory, file_name)

      try:
          with open(file_path, 'r') as f:
            print("File " + file_name + " found")
            #idx = convert_substring_to_integer(file_name,start_idx,end_idx)
            idx = extract_number_from_filename(file_name)
            print ("idx %d" %idx) 
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
                    
                    
              for i in range(len(lines)):
                if lines[i].find("VECTORS Contact_Forces float") != -1:
                    print("FOUND CONTACT FORCE. in line ", i, lines[i])
                    end = False    
                    i = i+2
                    line_ini_f = i
                    
                    while not end:
                        if lines[i].find("VECTORS") != -1:
                            lf = i - 2
                            end = True
                        i += 1
                                
                                
                                
              node_count = lf - line_ini -1
              print("Node Coount ", lf - line_ini + 1)
              first = False
            # print (lines[lf])
            #numbers_array = [float(num) for num in lines[lf].split()]
            
            #print ("LINE_INI: ", line_ini)
            force_z = 0.0
            force_tool_z = 0.0
            temps = []
            top_count = 0
            bot_count = 0
            for k in range (node_count) :
              #narr = [float(num) for num in lines[line_ini+k].split()]
              #print (k+line_ini)
              #print ("LINE VAL: "+lines[line_ini+k]+"\n")
              #print ("K",k, "line", line_ini+k)
              if ( k >= ini_node and k <end_node):                
                #print ("energy:",m_nod * c_p * (float(lines[line_ini+k]) - T0 ))
                force_tool_z += m_nod * c_p * (float(lines[line_ini+k]) - T0)
                T = 0
                T = float(lines[line_ini + k + ini_node])
                #print ("TEMP node ",k,": ",T)
                temps.append(T)

              if k >= ini_node_f and k < end_node_top_f:
                  narr = [float(num) for num in lines[line_ini_f+k].split()]
                  fn = narr[0]*narr[0]+narr[1]*narr[1]+narr[2]*narr[2] 
                  if (fn>0.0):
                    top_count += 1
                    #T = float(lines[line_ini_f + k + ini_node])
                    #print("Node ",k, " in contact, CF", narr, "line ",line_ini_f+k)
                    #cont_heat_sum +=


              if k >= (end_node_top_f+1) and k < end_node_f:
                  narr = [float(num) for num in lines[line_ini_f+k].split()]
                  fn = narr[0]*narr[0]+narr[1]*narr[1]+narr[2]*narr[2] 
                  if (fn>0.0):
                    bot_count += 1
                    #T = float(lines[line_ini_f + k + ini_node])
                    #print("Node ",k, " in contact, CF", narr, "line ",line_ini_f+k)
                    #cont_heat_sum +=
                                  
            print ("Nodes in contact ", top_count)
            
            temperatures[idx] = temps
            area_top [idx] = top_count * node_area
            area_bot [idx] = bot_count * node_area
            
            print("Area Top: ",area_top [idx], "Area Bot: ",area_bot [idx] )
            
            #print("Temp size", len(temps))
            #print("WRITING FORCE in idx", idx ,", vector size: ", len(force))
            force[idx] = force_tool_z

            #print ("Contact Force", numbers_array[0], numbers_array[1],numbers_array[2])
            #force.append(numbers_array[2])
            #force[idx] =  numbers_array[2]
            j += 1
      except Exception as e:
          print(f"Error opening {file_name}: {e}")
          
    useful_nc = end_node - ini_node 
    
    print("Node Count: ",node_count, "Useful nc: ",useful_nc)
    heat_vector = []
    cool_vector = []
    sorted_indices = sorted(temperatures.keys())
    #print ("Temperatures length: ",len(temperatures[2]))
    #print("First Node temp time 0, 1: ",temperatures[0][0],temperatures[1][0])
    print ("Writing temps")
    for i in range(1, len(sorted_indices)):
        prev_idx = sorted_indices[i - 1]
        curr_idx = sorted_indices[i]
        #print("Prev idx Curr idx: ",prev_idx,curr_idx)
        heat = 0.0
        cold = 0.0
        for k in range(useful_nc):
            if (k==0):
              print ("Node  ", k, "Curr temp ",temperatures[curr_idx][k],"Prev", temperatures[prev_idx][k])
            delta_T = temperatures[curr_idx][k] - temperatures[prev_idx][k]
            flow = m_nod * c_p * delta_T
            if (flow > 0.0):
              heat += flow
            else:
              cold += flow
              
        heat_vector.append(heat)
        cool_vector.append(cold)
        
    print("Areas",area_top)

    return heat_vector,cool_vector,area_top,area_bot, cont_heat
    
    
    
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
    
    heat, cold, area_top, area_bot, cont_heat = open_files_with_extension(directory, extension)

    write_list(heat, cold, area_top, area_bot, cont_heat)
