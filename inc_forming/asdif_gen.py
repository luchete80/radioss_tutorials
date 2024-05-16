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
largo = 0.22
delta = 0.004
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
gap_cont      = 1.7e-4
dtout         = 1.0e-4
end_time      = 2.1879884613e+00
v_supp        = 1.0e-3
supp_rel_time = 0.5
supp_vel_ramp = True
dynrel_time   = 2.0
## SCALING
vscal_fac     = 250.0 #Affects All magnitudes with s^-1: Tool Speed, HEAT CONDUCTIVIY, CONVECTION

###### SUPPORT
dens_supp_1 = 4
dens_supp_2 = 50
largo_supp = 0.01

###### CENTER OF PIECE 
x_init              = r_i  #DO NOT PUT xo! USED AS x OUTPUT IN DOUBLE SIDED
move_tool_to_inipos = True # THIS IS CONVENIENT, OTHERWISE RADIOSS THROWS ERROR DUE TO LARGE DISP TO INITIAL POS
thermal             = False
cont_support        = True       #TRUE: SUPPORT IS MODELED BY CONTACT, FALSE: SUPPORT IS MODELED BY BCS ON NODES
double_sided        = False
calc_path           = False
manual_mass_scal    = False


###### MATERIAL
mat = Material(1,thermal) #ID, THERMAL
mat.rho     = 7850.0
mat.E       = 200.0e9
mat.nu      = 0.33
mat.vs_fac  = vscal_fac

#thermal
mat.k_th  = 15.0 # 15 //
mat.cp_th = 419.11

mat.Ajc   = 359.0e6
mat.Bjc   = 327.0e6
mat.njc   = 0.454
mat.mjc   = 0.919
mat.Cjc   = 0.0786
mat.e0jc  = 0.04

##### SCALING
# class Scaling(Enum):
  # NONE   = 1       # 
  # VPROC  = 2       #Only on tool veloc 
  # MS_FIX = 3       #Fixed Mass scal, since cp 
  # VS_FIX = 4
  # AMS    = 5

# scal_type = Scaling.MS_FIX
# scal_fac  = 250.0          #ONLY WORKS WITH FIXE MS OR VS 

################################################## BEGIN ####################################################################################
#############################################################################################################################################
# if (scal_type == Scaling.NONE or scal_type == Scaling.VPROC or scal_type == Scaling.AMS):
  # scal_fac = 1.0

# filelbl = Label(window, text="Input File", width=15,justify=LEFT)
# filelbl.grid(column=1, row=0)	
# textField = Entry(window, width=15)
# textField.grid(column=2, row=0)
# textField.insert(0,"test")

test = [(1,1),(2,2)]
test.append((3,4))
print (test)
print (test[2][0])



supp_mesh = []
supp_part = []

shell_elnod = [(1,2,3,4)]


shell_mesh = Plane_Mesh(1,largo,delta)
if (not move_tool_to_inipos):
  x_init = 0.0
sph1_mesh = Sphere_Mesh(2, tool_rad-thck_rig/2.0,        \
                        x_init, 0.0,(tool_rad + thck/2.0 + gap + thck_rig), \
                                        5) #(id, radius, divisions):

if (double_sided):
  sph2_mesh = Sphere_Mesh(3, tool_rad-thck_rig/2.0,        \
                        0.0, 0.0,(-tool_rad - thck/2.0 - gap-thck_rig), \
                                        5) #(id, radius, divisions):
                                        

if (cont_support):
  #Y-     support,                id,lx,               ly,         elem_x,     elem_y,       ox,                   oy, z_, flip):
  supp_mesh.append(Rect_Plane_Mesh(4,largo+largo_supp,largo_supp,dens_supp_2,dens_supp_1, -largo/2.0-largo_supp/2.0, -largo/2.0-largo_supp/2.0, -thck/2.0-gap_cont-thck_supp/2.0, False)) #Legth x,  
  supp_mesh[0].AddRigidNode(0.0,-largo/2.0, -2.0*thck)
  supp_mesh.append(Rect_Plane_Mesh(5,largo+largo_supp,largo_supp,dens_supp_2,dens_supp_1, -largo/2.0-largo_supp/2.0, -largo/2.0-largo_supp/2.0,  thck/2.0+gap_cont+thck_supp/2.0, True))
  supp_mesh[1].AddRigidNode(0.0,-largo/2.0,  2.0*thck)

  #Y+ support,                   id,lx,               ly,         elem_x,     elem_y,       ox,                   oy, z_, flip):
  supp_mesh.append(Rect_Plane_Mesh(6,largo+largo_supp,largo_supp,dens_supp_2,dens_supp_1, -largo/2.0-largo_supp/2.0,  largo/2.0-largo_supp/2.0, -thck/2.0-gap_cont-thck_supp/2.0, False))
  supp_mesh[2].AddRigidNode(0.0, largo/2.0, -2.0*thck)
  supp_mesh.append(Rect_Plane_Mesh(7,largo+largo_supp,largo_supp,dens_supp_2,dens_supp_1, -largo/2.0-largo_supp/2.0,  largo/2.0-largo_supp/2.0,  thck/2.0+gap_cont+thck_supp/2.0, True))
  supp_mesh[3].AddRigidNode(0.0, largo/2.0,  2.0*thck)
  
  #THESE SUPPORTS HAVE Y LENGTH SHORTER THAN OTHERS; ONLY Y LENGTH ON HEIGHT
  # #X-     support,                id,lx,      ly,     elem_x,     elem_y,       ox,               oy, z_, flip):  
  x_pos = largo/2.0
  supp_mesh.append(Rect_Plane_Mesh(8,largo_supp,largo-largo_supp,dens_supp_1,dens_supp_2, -x_pos-largo_supp/2.0, -largo/2.0+largo_supp/2.0, -thck/2.0-gap_cont-thck_supp/2.0, False))
  supp_mesh[4].AddRigidNode(-largo/2.0 ,0.0,  -2.0*thck)
  supp_mesh.append(Rect_Plane_Mesh(9,largo_supp,largo-largo_supp,dens_supp_1,dens_supp_2, -x_pos-largo_supp/2.0, -largo/2.0+largo_supp/2.0,  thck/2.0+gap_cont+thck_supp/2.0, True))
  supp_mesh[5].AddRigidNode(-largo/2.0 ,0.0,   2.0*thck)
  

  # #X+     support,                id,lx,      ly,     elem_x,     elem_y,       ox,               oy, z_, flip):  
  supp_mesh.append(Rect_Plane_Mesh(10,largo_supp,largo-largo_supp,dens_supp_1,dens_supp_2, x_pos-largo_supp/2.0, -largo/2.0+largo_supp/2.0, -thck/2.0-gap_cont-thck_supp/2.0, False))
  supp_mesh[6].AddRigidNode(-largo/2.0 ,0.0,  -2.0*thck)
  supp_mesh.append(Rect_Plane_Mesh(11,largo_supp,largo-largo_supp,dens_supp_1,dens_supp_2, x_pos-largo_supp/2.0, -largo/2.0+largo_supp/2.0,  thck/2.0+gap_cont+thck_supp/2.0, True))
  supp_mesh[7].AddRigidNode(-largo/2.0 ,0.0,   2.0*thck)


  
print("Piece Shell node count", len(shell_mesh.nodes))
# print("Shell Shell node count", len(sph1_mesh.nodes))

print("Shell node count: ", shell_mesh.node_count)
# print("Sphere node count var", sph1_mesh.node_count)

if (double_sided):
  print("Sphere 2 node count:", sph2_mesh.node_count)

# print("Shell node count", len(shell_mesh.elnod))
# print("Shell node count", len(sph1_mesh.elnod))

model = Model()
model.end_proc_time = end_time
model.double_sided = double_sided
print ("Model size: ", len(model.part))
shell = Part(1)
shell.AppendMesh(shell_mesh) 
model.vscal_fac = vscal_fac

bcpos = largo/2.0 - largo_supp

sph1_pt = Part(2)
sph1_pt.AppendMesh(sph1_mesh) 
sph1_pt.is_rigid = True
sph1_pt.is_moving = True
sph1_pt.asignPropID(2)

if (double_sided):
  sph2_pt = Part(3)
  sph2_pt.AppendMesh(sph2_mesh) 
  sph2_pt.is_rigid = True
  sph2_pt.is_moving = True
  sph2_pt.asignPropID(2)

model.AppendPart(shell) #FIRST PART TO ADD!

if (cont_support):
  for sp in range (2*4):
    supp_part.append(Part(4+sp))
    supp_part[sp].AppendMesh(supp_mesh[sp])
    supp_part[sp].is_rigid = True #REMEMBER LAST NODE OF THE PART IS THE PIVOT
    supp_part[sp].asignPropID(3)
    print("support part length", len(supp_part))
    model.AppendPart(supp_part[sp])

if (not cont_support):
  model.AddNodeSetOutsideBoxXY(1000,Vector(-bcpos,-bcpos,0.0), Vector(bcpos,bcpos,0.0)) #id, v1, v2):

model.AppendPart(sph1_pt)
if (double_sided):
  model.AppendPart(sph2_pt)

model.AppendMat(mat)
model.AppendProp(Prop(1,thck))

model.AppendProp(Prop(2,thck_rig))

model.AppendProp(Prop(3,thck_supp))

#BALLS AND PLATE
inter_1 = Interface(2,1)
model.AppendInterface(inter_1)

if (double_sided):
  inter_2 = Interface(3,1)
  model.AppendInterface(inter_2)

#CHANGE TO ARRAY
if (cont_support):
  for sp in range (2*4):
    model.AppendInterface(Interface(sp+4,1))
  
  
model.cont_support = cont_support



if (thermal):
  model.part[0].mesh[0].print_segments = True #THERMAL SEGMENTS, RESERVED IDS TO PARTS

if (thermal):
  model.thermal = True

# THERMAL
for e in range (model.part[0].mesh[0].elem_count):
  lf = Function(0.0,.0,0)
  model.AppendLoadFunction (lf)
# sphere_mesh = Sphere_Mesh(2,1.0, 10,1) #(self, id, radius, divisions, ininode):

# shell_mesh.printRadioss("radioss.rad")

# sphere_mesh.printRadioss("radioss.rad")

#IMPORTANTE: LA VELOCIDAD SE ASUME PARA RADIO CONSTANTE EN CADA VUELTAS
#CON LO CUAL EN LA REALIDAD DISMINUYE UN POCO
# def save(lin):

if (calc_path):
# f= open(textField.get(),"w+")
  # LA HERRAMIENTA INTERNA ESTA EN EL TOP, LA EXTERNA EN EL BOTTOM
  # PERO TOP Y BOTTOM CONFUNDE POR LAS INDENTACIONES
  fi_x = open("movi_x.inc","w")
  fi_y = open("movi_y.inc","w")
  fi_z = open("movi_z.inc","w")

  if (double_sided):  
    fo_x = open("movo_x.inc","w")
    fo_y = open("movo_y.inc","w")
    fo_z = open("movo_z.inc","w")

  fi_x.write("/FUNCT/1000001\nmovx\n")    
  fi_y.write("/FUNCT/1000002\nmovy\n")      
  fi_z.write("/FUNCT/1000003\nmovz\n")    

  if (double_sided):
    fo_x.write("/FUNCT/1000004\nmovx\n")    
    fo_y.write("/FUNCT/1000005\nmovy\n")      
    fo_z.write("/FUNCT/1000006\nmovz\n")    
  
  t = 0.0
  r = r_i
  turn = 1
  
  z  = 0.0 
  # zo = -thck #ESTA HERRAMIENTA NO DESCIENDE (PARA EVITAR DEFORMACIONES IRREGULARES)
  # zi =  thck 
  zo = zi = 0
  vz = (thck + p_S) / t_ind # EN PRINCIPIO S EDESPLAZA SOLO LA INTERIOR 
  
  #####################INDENTACION ######################### 
  xi = r - p_D/2.0
  xo = r + p_D/2.0
  
  while (t < t_ind):    
    if (move_tool_to_inipos):
      xo -= x_init
      xi -= x_init

    zi -= vz * dt
    #HAY QUE VER SI ES NECESARIO ESCRIBIR X E Y PARA TODOS LOS TIEMPOS
    fi_x.write(writeFloatField(t,20,6) + writeFloatField(xi,20,6) + "\n")
    fi_y.write(writeFloatField(t,20,6) + writeFloatField(0.,20,6) + "\n")
    fi_z.write(writeFloatField(t,20,6) + writeFloatField(zi,20,6) + "\n")
    
    if (double_sided):
      fo_x.write(writeFloatField(t,20,6) + writeFloatField(xo,20,6) + "\n")
      fo_y.write(writeFloatField(t,20,6) + writeFloatField(0.,20,6) + "\n")
      fo_z.write(writeFloatField(t,20,6) + writeFloatField(zo,20,6) + "\n")
    
    # fo_x.write("%.6e, %.6e\n" % (t,xo))
    # fo_y.write("%.6e, %.6e\n" % (t,0.0))
    # fo_z.write("%.6e, %.6e\n" % (t,zo))  
    t +=dt 
 
  print("Final zi %.3e , zo %.3e \n" %(zi,zo))
  
  ######################## VUELTAS ##############################
  while (t < end_time):
    t_ang = 2.0 * pi * r / tool_speed #Tiempo (incremento) de cada vuelta (ASUMIENDO RADIO CONSTANTE)
    print("Turn %d Turn Time %.3e Time %.3e Radius %.3e\n" %(turn, t_ang,t,r))
    t_vuelta = t + t_ang  #Tiempo de final de vuelta (TOTAL)
    t_0 = t               #Tiempo de comienzo de vuelta
    t_inc = 0.0           # t - t_0
    dz = dr               #CAMBIAR SEGUN GEOMETRIA
    vz = dz / t_ang
    while (t < t_vuelta): #VUELTAS  
      # print ("t_inc %.3e t_ang %.3e"%(t_inc,t_ang))
      xi = (r - p_D/2.0 + dr * t_inc/t_ang) *cos(2.0*pi*t_inc/t_ang)
      yi = (r - p_D/2.0 + dr * t_inc/t_ang) *sin(2.0*pi*t_inc/t_ang)
      zi -= vz * dt

      xo = (r + p_D/2.0 + dr * t_inc/t_ang) *cos(2.0*pi*t_inc/t_ang)
      yo = (r + p_D/2.0 + dr * t_inc/t_ang) *sin(2.0*pi*t_inc/t_ang)      
      zo -= vz * dt #CAMBIAR A DZ
      
      # print("zi %.3e , zo %.3e \n" %(zi,zo))
      # z -= t_inc/t_ang * dr # CAMBIAR A dz
      
      fi_x.write(writeFloatField(t,20,6) + writeFloatField(xi,20,6) + "\n")
      fi_y.write(writeFloatField(t,20,6) + writeFloatField(yi,20,6) + "\n")
      fi_z.write(writeFloatField(t,20,6) + writeFloatField(zi,20,6) + "\n")
      if (double_sided):
        fo_x.write(writeFloatField(t,20,6) + writeFloatField(xo,20,6) + "\n")
        fo_y.write(writeFloatField(t,20,6) + writeFloatField(yo,20,6) + "\n")
        fo_z.write(writeFloatField(t,20,6) + writeFloatField(zo,20,6) + "\n")
      
      # fo_x.write("%.6e, %.6e\n" % (t,xo))
      # fo_y.write("%.6e, %.6e\n" % (t,yo))
      # fo_z.write("%.6e, %.6e\n" % (t,zo))
      
      t_inc +=dt
      t += dt

      if (thermal):
        e = model.part[0].mesh[0].findNearestElem(xi,yi,zi)
        flog.write ("TIME %f, pos: %.6e %.6e, Found %d\n" % (t, xi, yi, e ))
        coord = str (model.part[0].mesh[0].elcenter[e].components)
        flog.write ("baricenter: %s\n" %(coord))  
        model.load_fnc[e].Append(t,1.0e6)
      
    r +=dr
    turn += 1    

  #SPRINGBACK
  fi_x.close;fi_y.close;fi_z.close
  if (double_sided):
    fo_x.close;fo_y.close;fo_z.close

              #filename, name, id, init_time, veloc):
f_upper_supp = Function(1000007,0.0,0.0) 
f_upper_supp.Append(end_time, 0.0)
if (not supp_vel_ramp):
  f_upper_supp.Append(end_time+1.0e-4, v_supp)
f_upper_supp.Append(end_time+supp_rel_time, v_supp)
f_upper_supp.Append(end_time+supp_rel_time+1.0e-4,  10.0*v_supp)
f_upper_supp.Append(end_time+supp_rel_time+1.0e-4+dynrel_time,      10.0*v_supp)
model.supp_fnc.append(f_upper_supp)


  
for e in range (model.part[0].mesh[0].elem_count):  
  model.load_fnc[e].Append(1.0e3,0.0)



# for e in range (10):
  # # for f in range (len(load_function[e])):
  # for f in range (model.load_fnc[e].val_count):
    # print ("Load Fnction ", e, model.load_fnc[e].getVal(f))
  

model.printRadioss("test")

model.printEngine(1, end_time,dtout)
model.printRelease(2, end_time+supp_rel_time,dtout)
model.printDynRelax(3,end_time+supp_rel_time+dynrel_time,dtout)
# #Si no se coloca lambda no funciona
# b = Button(window, text="Generate", width=10, command=lambda:save(linea_g))
# b.grid(column=3, row=10)
# #b.pack()

# window.title('Incremental Forming PATH Script')
# window.geometry("400x200+10+10")
# window.mainloop()
