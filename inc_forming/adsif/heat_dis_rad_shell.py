import numpy as np
import os
import re 
import math

ini_node = 0
end_node = 63000
#node_count = end_node-ini_node +1 

nsides = 251
node_count = nsides * nsides

largo_supp = 0.01

start_index = 5
end_index = 7 

T0 = 293.0
thck = 5.0e-4
L = 0.1
dens = 4430.0
c_p = 520.0
sigma = 5.670374419E-8 #W/m2K4
eps = 0.35

print("Average Elem area: ", L/(nsides-1)*L/(nsides-1))



def extract_number_from_filename(filename):
    match = re.search(r'\d+', filename)  # busca la primera secuencia de dígitos
    if match:
        return int(match.group())
    return None


def write_list(atop, cheat):
  fi_x = open("energy_rad.csv","w")
  fi_x.write("t,area,heat\n")

  dt = 1.0
  t = 0.0
  for i in range(len(atop)-1):
    fi_x.write(str(t) + ", " + str(atop [i])+ ","+str(cheat [i])+ "\n" )
    t +=dt

def build_element_connectivity(n, node_count):
    
    nx = ny = n
    print(f"Dimensiones de la malla: {nx} x {ny}")
    
    # Construir conectividad para elementos cuadriláteros (en 2D) o hexaedros (en 3D)
    elements = []
    element_nodes = {}
    node_elements = {}
    
    # Inicializar node_elements con listas vacías para todos los nodos
    for i in range(node_count):
        node_elements[i] = []
    
    # Para malla 2D estructurada, elementos son cuadriláteros
    for j in range(ny-1):
        for i in range(nx-1):
            n1 = j * nx + i
            n2 = j * nx + i + 1
            n3 = (j+1) * nx + i + 1
            n4 = (j+1) * nx + i
            
            elem_id = len(elements)
            elements.append([n1, n2, n3, n4])
            element_nodes[elem_id] = [n1, n2, n3, n4]
            if (len(elements) == 32127):
              print("Elem ", elem_id, "Nodes",element_nodes[elem_id])
            
            node_elements[n1].append(elem_id)
            node_elements[n2].append(elem_id)
            node_elements[n3].append(elem_id)
            node_elements[n4].append(elem_id)
    
    # ~ print("Node 0 elements", node_elements[0])
    # ~ print("Node 32127 elements", node_elements[32127])
          
    
    return elements, element_nodes, node_elements

def calculate_element_area(nodes, element_id, element_nodes, all_nodes):
    """Calcula el área de un elemento basado en sus nodos"""
    node_indices = element_nodes[element_id]
    
    if len(node_indices) == 4:  # Elemento cuadrilátero (2D)
        # Obtener coordenadas de los nodos
        coords = [all_nodes[node_idx] for node_idx in node_indices]
        
        # Calcular área usando el método del producto cruzado para cuadriláteros
        # Dividir el cuadrilátero en dos triángulos y sumar sus áreas
        area1 = 0.5 * abs(
            (coords[2][0] - coords[0][0]) * (coords[1][1] - coords[0][1]) -
            (coords[1][0] - coords[0][0]) * (coords[2][1] - coords[0][1])
        )
        area2 = 0.5 * abs(
            (coords[2][0] - coords[0][0]) * (coords[3][1] - coords[0][1]) -
            (coords[3][0] - coords[0][0]) * (coords[2][1] - coords[0][1])
        )
        return area1 + area2
    
    elif len(node_indices) == 8:  # Elemento hexaédrico (3D)
        # Para elementos 3D, calculamos el área de la cara en contacto
        # Esto es más complejo y depende de qué cara está en contacto
        # Por simplicidad, asumimos que calculamos el área de una cara
        # Tomamos los primeros 4 nodos que forman una cara
        coords = [all_nodes[node_idx] for node_idx in node_indices[:4]]
        
        # Calcular área de la cara cuadrilátera
        area1 = 0.5 * abs(
            (coords[2][0] - coords[0][0]) * (coords[1][1] - coords[0][1]) -
            (coords[1][0] - coords[0][0]) * (coords[2][1] - coords[0][1])
        )
        area2 = 0.5 * abs(
            (coords[2][0] - coords[0][0]) * (coords[3][1] - coords[0][1]) -
            (coords[3][0] - coords[0][0]) * (coords[2][1] - coords[0][1])
        )
        return area1 + area2
    
    return 0.0

def calculate_nodal_area_for_node(node_id, node_elements, element_nodes, all_nodes):
    """Calcula el área nodal para un nodo específico sumando las contribuciones proporcionales de elementos adyacentes"""
    nodal_area = 0.0
    
    # Obtener todos los elementos que comparten este nodo
    element_ids = node_elements.get(node_id, [])
    
    for elem_id in element_ids:
        # Calcular área del elemento
        element_area = calculate_element_area(None, elem_id, element_nodes, all_nodes)
        
        # Dividir el área del elemento entre el número de nodos que lo componen
        num_nodes_in_element = len(element_nodes[elem_id])
        nodal_area += element_area / num_nodes_in_element
    
    return nodal_area

def read_node_coordinates(vtk_file_path):
    """Lee las coordenadas de los nodos desde un archivo VTK"""
    with open(vtk_file_path, 'r') as f:
        lines = f.readlines()
    
    coordinates = []
    reading_points = False
    point_count = 0
    
    for i, line in enumerate(lines):
        if line.startswith('POINTS'):
            point_count = int(line.split()[1])
            reading_points = True
            continue
        
        if reading_points:
            parts = line.split()
            for j in range(0, len(parts), 3):
                if len(parts) >= j+3:
                    x = float(parts[j])
                    y = float(parts[j+1])
                    z = float(parts[j+2])
                    coordinates.append((x, y, z))
            
            if len(coordinates) >= point_count:
                break
    print("Point Count: ",point_count)
    return coordinates
        

def open_files_with_extension(directory, extension):
    if not os.path.isdir(directory):
        print(f"Directory '{directory}' does not exist.")
        return
    
    files = [f for f in os.listdir(directory) if f.endswith(extension)]
    
    if not files:
        print(f"No files found with '{extension}' extension in '{directory}'.")
        return
    
    print("Found %d files " % len(files))
    
    # Ordenar archivos por número
    files.sort(key=extract_number_from_filename)
    
    # Leer el primer archivo para construir la conectividad
    first_file = files[0]
    first_file_path = os.path.join(directory, first_file)
    
    # Leer coordenadas de nodos y construir conectividad
    node_coords = read_node_coordinates(first_file_path)
    elements, element_nodes, node_elements = build_element_connectivity(nsides, node_count)

    # Obtener el índice máximo de todos los archivos
    max_idx = 0
    for file_name in files:
        idx = extract_number_from_filename(file_name)
        if idx is not None and idx > max_idx:
            max_idx = idx
    
    print(f"Maximum index found: {max_idx}")
        
    force = np.zeros(max_idx+1)  # index begins with 1
    temperatures = {}
    area_top = np.zeros(max_idx+1)
    cont_heat = np.zeros(max_idx+1)
    
    first = True
    tot = len(files)
    
    for j, file_name in enumerate(files, 1):
        cont_heat_sum = 0.0
        file_path = os.path.join(directory, file_name)
        
        try:
            with open(file_path, 'r') as f:
                print("File " + file_name + " found")
                idx = extract_number_from_filename(file_name)
                print("idx %d" % idx)
                lines = f.readlines()
                print("file " + str(j) + "/" + str(tot))
                
                if first:
                    # Encontrar la posición de los datos de temperatura y fuerzas
                    temp_line_ini = None
                    force_line_ini = None
                    
                    for i in range(len(lines)):
                        if lines[i].find("SCALARS Nodal_Temperature float 1") != -1:
                            temp_line_ini = i + 2
                        
                        if lines[i].find("VECTORS Contact_Forces float") != -1:
                            force_line_ini = i + 2
                    
                    first = False
                #print("Line Count: ", len(lines), ", Force Line Ini: ", force_line_ini,", Temp Line Ini: ", temp_line_ini)
                # Leer temperaturas
                temps = []
                for k in range(len(node_coords)):
                    if temp_line_ini + k < len(lines):
                        temps.append(float(lines[temp_line_ini + k].strip()))
                

                temperatures[idx] = temps

                nod_area = 0.0 #For comparison
                for node in range(ini_node, end_node):
                    area = calculate_nodal_area_for_node(node, node_elements, element_nodes, node_coords)
                    #print ("Node ", node, " Temp ",float(lines[temp_line_ini + node]), ", Area: ",  area)
                    power = eps * area * sigma * ( float(lines[temp_line_ini + node])**4 -  T0**4) 
                    cont_heat[idx] += power
                    nod_area += area

                area_top[idx] = nod_area *1.0e6
              
        
                print("Contact Area Elemental : ", area_top[idx], "Nodal: ", nod_area*1.0e6, "Heat: ", cont_heat[idx])
                

        
                
        except Exception as e:
            print(f"Error opening {file_name}: {e}")
            
    print("Contact Heat: ", cont_heat[idx] )
            
    
    return  area_top, cont_heat

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
    
    area_top, cont_heat = open_files_with_extension(directory, extension)

    write_list( area_top, cont_heat)
