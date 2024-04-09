import numpy as np
import os



start_index = 5
end_index = 7 

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
  fi_x = open("force.csv","w")
  fi_x.write("t,f\n")

  dt = 1.0e-3
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
    force = np.zeros(len(files))

    
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
                if (lines[i].find("VECTORS Sect.RBY,Wall_F. float") != -1):
                  # print("FOUND STRING. in line ", i, lines[i])
                  end = False    
                  i = i+1
                  
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
              first = False
            # print (lines[lf])

            numbers_array = [float(num) for num in lines[lf].split()]

            print ("Force", numbers_array[0], numbers_array[1],numbers_array[2])
            #force.append(numbers_array[2])
            force[idx] =  numbers_array[2]
            j += 1
      except Exception as e:
          print(f"Error opening {file_name}: {e}")
    return force
          
###### INPUT PARAM ENTRADA ##############

# directory = '/path/to/directory'
directory = '.'
extension = '.vtk'  # Change this to the extension you want to search for

force = open_files_with_extension(directory, extension)
write_list(force)