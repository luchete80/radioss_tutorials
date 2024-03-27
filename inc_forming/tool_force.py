import numpy as np
import os

force = []

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
    
    first = True 
    print("File " + files[0] + " found")
    # Open each file
    for file_name in files:
        file_path = os.path.join(directory, file_name)
        try:
            with open(file_path, 'r') as f:
              lines = f.readlines()
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
                        print("found next VECTORS in line ",i)
                        # print (lines[j-2])
                        lf = i - 2
                        end = True
                      # print (i)
                      i +=1
                first = False
              # print (lines[lf])

              numbers_array = [float(num) for num in lines[lf].split()]

              # print (numbers_array[2])
              force.append(numbers_array[2])
        
        except Exception as e:
            print(f"Error opening {file_name}: {e}")
            
###### INPUT PARAM ENTRADA ##############

# directory = '/path/to/directory'
directory = '.'
extension = '.vtk'  # Change this to the extension you want to search for

open_files_with_extension(directory, extension)

fi_x = open("force.csv","w")
fi_x.write("t,f\n")

dt = 1.0e-3
t = 0.0
for i in range(len(force)):
  fi_x.write(str(t) + ", " + str(force [i]) + "\n" )
  print(force [i])
  t +=dt
