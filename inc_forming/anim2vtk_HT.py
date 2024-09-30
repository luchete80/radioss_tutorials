import glob
import numpy as np
import os
import threading
import sys
import time

def find_files(file_masks):
    filefound = []
    for file_mask in file_masks:
        f(file_mask))
    return filefound

def split_into_sublists(lst, sublist_size):
    sublists = []
    for i in range(0, len(lst), sublist_size):
        sublists.append(lst[i:i + sublist_size])
    return sublists

def anim2vtk(files):
    for file_name in files:
        print("File " + file_name + " found")
        os.system("anim_to_vtk_win64.exe "  + file_name  + " > " + file_name + ".vtk")        
        
def tarea(thread_id,files):
    print(f"Thread {thread_id}: Iniciando tarea")
    anim2vtk(files)  # Simulación de una tarea que toma 2 segundos
    print(f"Thread {thread_id}: Tarea completada")
    
def split_list(lst, m,start_file=0):
    lst=lst[start_file:]
    sublist_size = len(lst) // m
    remainder = len(lst) % m
    sublists = []
    start = 0
    for i in range(m):
        sublist_length = sublist_size + (1 if i < remainder else 0)
        end = start + sublist_length
        sublists.append(lst[start:end])
        start = end
    return sublists


def anim2vtk_HT(cores=2,start_file=0):
    # Crear lista de arrhivos segur expresión regular
    file_masks = ["testA[0-9][0-9][0-9]"]
    files = find_files(file_masks)
    file_masks = ["testA[0-9][0-9][0-9][0-9]"]
    
    files=files+find_files(file_masks)
    total_files=len(files)
    
    print("Found %d files " %len(files))
    
    file_group=split_list(files,cores,start_file)   
    print("grouped in %d list of files " %len(file_group))    
    
    start_time = time.time()
    
    threads = []
    for i,files in enumerate(file_group[:]):
        thread = threading.Thread(target=tarea, args=(i,files))
        threads.append(thread)
        thread.start()
    
    # Esperar a que todos los threads terminen
    for thread in threads:
        thread.join()
    
    print("Todos los threads han terminado para %s archivos",total_files)
    print("--- %s seconds ---" % (time.time() - start_time))

def main():
    if len(sys.argv) < 2:
        #print("script_anim2vtk.py <cores> [start_file]")
        sys.exit(1)

    try:
        cores = int(sys.argv[1])

        # Si se proporciona start_file, lo convertimos a entero; si no, lo inicializamos en 0
        if len(sys.argv) >= 3:
            start_file = int(sys.argv[2])
        else:
            start_file = 0
        # call w/cores & start_file
        anim2vtk_HT(cores, start_file)

    except ValueError:
        print("cores & start_file must be integer")
        sys.exit(1)
    except Exception as e:
        print(f"Error al ejecutar anim2vtk: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


