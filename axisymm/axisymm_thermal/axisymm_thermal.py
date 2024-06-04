#https://www.tutorialsteacher.com/python/create-ui-using-tkinter-in-python
from math import *
from mesher import *
import numpy as np

# from tkinter import *
# from tkinter.ttk import Combobox
from enum import Enum

# window=Tk()
linea_g=10

flog = open("log.txt","w")

#################### INPUT VARS

#WORKPIECE
radio = 0.15
largo = 0.616
delta = 0.005
thck  = 6.5e-4      #Plate Thickness
thck_rig = 1.0e-4   #BALL
thck_supp = 1.0e-3  #SUPP

#TOOL 
r_i           = 88.2414e-3      #Inner Path Radius
r_o           = 0.0325    #Outer Path Radius
r             = 0.0325
dr            = 5.0e-4    #DESAPARECE DE ACUERDO A LA GEOMETRIA
dt            = 1.0e-5    #Time increment for path gen
#t_ang         = 1.0e-3    #Periodo angular, ANTES ERA CONSTANTE
p_D           = 2.5e-3     #ASDIF RADIAL DISTANCE BETWEEN TOOLS
p_S           = 4.3e-4     #ASDIF HEIGHT DISTANCE BETWEEN TOOLS
tool_speed    = 0.6 / 60.0 * 5000 #600mm/min according to Valoppi
t_ind         = 1.0e-3
tool_rad      = 0.00755    #Tool radius
gap           = 0.0e-4
gap_cont      = 1.3e-4
dtout         = 5.0e-3
end_time      = 2.1879884613e+00
v_supp        = 1.0e-3
supp_rel_time = 0.5
supp_vel_ramp = True
dynrel_time   = 2.0
## SCALING
vscal_fac     = 250.0 #Affects All magnitudes with s^-1: Tool Speed, HEAT CONDUCTIVIY, CONVECTION

mat = Material(1,True) #ID, THERMAL
#thermal
mat.k_th  = 15.0 # 15 //
mat.cp_th = 419.11


test = [(1,1),(2,2)]
test.append((3,4))
print (test)
print (test[2][0])



supp_mesh = []
supp_part = []

shell_elnod = [(1,2,3,4)]


# shell_mesh = Plane_Mesh(1,largo,delta)

#Rect_Plane_Mesh(self, id, lx, ly, elem_x, elem_y, ox, oy, flip)
shell_mesh = Rect_Plane_Mesh(1,radio,largo,int(radio/delta),int(largo/delta),0.0,0.0,False)


print("Shell node count: ", shell_mesh.node_count)
# print("Sphere node count var", sph1_mesh.node_count)

model = Model()
model.end_proc_time = end_time

print ("Model size: ", len(model.part))
shell = Part(1)
shell.AppendMesh(shell_mesh) 
model.vscal_fac = vscal_fac

model.AppendMat(mat)

model.AppendPart(shell) #FIRST PART TO ADD!

  

model.printRadioss("test")

model.printEngine(1, end_time,dtout)

