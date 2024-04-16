import numpy as np
import os

import subprocess


def open_files_with_extension(directory, extension):
    # Check if the directory exists
    if not os.path.isdir(directory):
        print(f"Directory '{directory}' does not exist.")
        return
    
    # Get a list of files with the specified extension
    files = [f for f in os.listdir(directory) if f.startswith(extension)]
    
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
      # start_idx = find_integer_substring_indices(file_name)
      # end_idx = find_integer_substring_end_indices(file_name)
      # print("start: " + str(start_idx) + ", end " + str(end_idx))
      file_path = os.path.join(directory, file_name)

      try:
          with open(file_path, 'r') as f:
            print("File " + file_name + " found")
            os.system("anim_to_vtk_linux64_gf "  + file_name  + " > " + file_name + ".vtk")
      except Exception as e:
          print(f"Error opening {file_name}: {e}")
    return force
          
###### INPUT PARAM ENTRADA ##############

# directory = '/path/to/directory'
directory = '.'
extension = 'testA'  # Change this to the extension you want to search for

open_files_with_extension(directory, extension)
