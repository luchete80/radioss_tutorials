#https://www.tutorialsteacher.com/python/create-ui-using-tkinter-in-python
from math import *
from mesher_solid import *
import numpy as np
import csv

# from tkinter import *
# from tkinter.ttk import Combobox
from enum import Enum

# window=Tk()
linea_g=10

flog = open("log.txt","w")

#################### INPUT VARS

#WORKPIECE
largo = 0.08
delta = 0.001
thck  = 5.0e-4      #Plate Thickness
thck_rig = 1.0e-4   #BALL
thck_supp = 1.0e-3  #SUPP
mech = False
vscal_fac     = 2000.0 #Affects All magnitudes with s^-1: Tool Speed, HEAT CONDUCTIVIY, CONVECTION

#TOOL 
r_i           = 5.1118e-3      #Inner Path Radius
r_o           = 5.3532e-3    #Outer Path Radius
# SHAPE FROM
#A hybrid mixed double-sided incremental forming method for forming
#Ti6Al4V alloy
###### -------------------------------------------------------------
# TOOL PATH GENERATION
#--------------------------------------------------------------------
r_ac1 = 5.0e-3 
r_ac2 = 5.0e-3
r_ac3 = 5.0e-3
ang_1 = 20.0 #DEG
ang_1 = 50.0 #DEG
tool_speed    = 0.6 / 60.0 * vscal_fac #Exam,ple 4000 mm/min 
t_ind         = 1.0e-3
dz_up         = 0.0
dz            = 1.0e-4    
dtind         = 0.01/vscal_fac    #Indentation time for crve generation
#!!!_ IMPORTANT THIS CAN BE enlarged if not thermal
da            = 1.0 #ANGLE FOR delta t in process. 
calc_path           = False
move_tool_to_inipos = True # THIS IS CONVENIENT, OTHERWISE RADIOSS THROWS ERROR DUE TO LARGE DISP TO INITIAL POS
ball_gap      = 1.0e-4  #THIS IS ASSIGNED SINCE IF NOT THE BALL INITIAL MOVEMENT DRAGS THE PLATE
r0            = 0.005

#dang           = 5.0  #Angle (deg) increment for path gen
p_D           = 2.5e-3     #ASDIF RADIAL DISTANCE BETWEEN TOOLS
p_S           = 4.3e-4     #ASDIF HEIGHT DISTANCE BETWEEN TOOLS

tool_rad      = 0.0025    #Tool radius
gap           = -8.0e-5
gap_cont      = -2.0e-4
dtout         = 5.0e-4
dtout_his     = 1.0e-4
### --- ONLY USED WHEN NOT GENERATING PATH !!!
end_time      = 2.0e-3
v_supp        = 1.0e-3
supp_rel_time = 0.5
supp_vel_ramp = True
dynrel_time   = 2.0
is_ASDIF      = True
## SCALING


###### SUPPORT
dens_supp_1 = 4
dens_supp_2 = 50
largo_supp = 0.0050

###### CENTER OF PIECE 
x_init              = r_i  #DO NOT PUT xo! USED AS x OUTPUT IN DOUBLE SIDED
x_init_o            = r_o  #DO NOT PUT xo! USED AS x OUTPUT IN DOUBLE SIDED
move_tool_to_inipos = True # THIS IS CONVENIENT, OTHERWISE RADIOSS THROWS ERROR DUE TO LARGE DISP TO INITIAL POS

thermal             = True
cont_support        = False       #TRUE: SUPPORT IS MODELED BY CONTACT, FALSE: SUPPORT IS MODELED BY BCS ON NODES
double_sided        = True
manual_mass_scal    = False


#FROM XIAN 
# Optimization on the Johnson-Cook parameters of
# Ti-6Al-4V used for high speed cutting simulation
###### MATERIAL
mat = Material(1,thermal) #ID, THERMAL
mat.mech    = True
mat.rho     = 4430.0
mat.E       = 105.0e9
mat.nu      = 0.34
mat.vs_fac  = vscal_fac

#thermal
mat.k_th  = 7.4 # 15 //
mat.cp_th = 520.0 #J/(kgK)


#From Optimization on the Johnson-Cook parameters of
#Ti-6Al-4V used for high speed cutting simulation
mat.Ajc   = 790.0e6
mat.Bjc   = 478.0e6
mat.njc   = 0.28
mat.mjc   = 1.0
mat.Cjc   = 0.032
mat.e0jc  = 1.0

supp_mesh = []
supp_part = []

shell_elnod = [(1,2,3,4)]

topfname = "myToolpath_topToolTipPnts.csv"
botfname = "myToolpath_botToolTipPnts.csv"

##### THERMAL HEAT GEN
t_interf = 1.0
vel = 600.0; #mm/min
av_dist = 0.9
dt = av_dist  / vel

#shell_mesh = Plane_Mesh(1,largo,delta)

solid_mesh = Rect_Solid_Mesh(1,largo,largo,thck,delta,delta,thck,-largo/2.0, -largo/2.0, -thck/2.0)

shell_mesh = Plane_Mesh(1,largo,delta)

if (mech):
    

  if (not move_tool_to_inipos):
    x_init = 0.0
  sph1_mesh = Sphere_Mesh(2, tool_rad,        \
                          x_init, 0.0,(tool_rad + thck/2.0 + gap + thck_rig/2.0), \
                                          5) #(id, radius, divisions):

  if (double_sided):
    sph2_mesh = Sphere_Mesh(3, tool_rad,        \
                          x_init_o, 0.0,(-tool_rad - thck/2.0 - gap-thck_rig/2.0), \
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


  if (double_sided):
    print("Sphere 2 node count:", sph2_mesh.node_count)

  
print("Piece Shell node count", len(solid_mesh.nodes))
# print("Shell Shell node count", len(sph1_mesh.nodes))

print("Solid node count: ", solid_mesh.node_count)
# print("Sphere node count var", sph1_mesh.node_count)



# print("Shell node count", len(shell_mesh.elnod))
# print("Shell node count", len(sph1_mesh.elnod))

model = Model()
model.mech = mech
model.double_sided = double_sided
print ("Model size: ", len(model.part))
shell = Part(1)
shell.AppendMesh(solid_mesh)
shell.asignPropID(1)
 
model.vscal_fac = vscal_fac

bcpos = largo/2.0 - largo_supp
if (mech):
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

if (mech):
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
model.AppendProp(Prop(1,"solid", 0))

if (mech):
  model.AppendProp(Prop(2,"shell", thck_rig))
  model.AppendProp(Prop(3,"shell", thck_supp))

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


# SOLID MODEL --------------------------------------------------------
th_solid_model = ThermalSolidModel()
solid_pt =Part(1)
solid_pt.AppendMesh(solid_mesh)


th_solid_model.AppendPart(solid_pt)
th_solid_model.AppendMat(mat)

if (calc_path):
  fi_x = open("movi_x.inc","w")
  fi_y = open("movi_y.inc","w")
  fi_z = open("movi_z.inc","w")

  f_test = open("tool_i.csv","w")

   
  fo_x = open("movo_x.inc","w")
  fo_y = open("movo_y.inc","w")
  fo_z = open("movo_z.inc","w")

# f= open(textField.get(),"w+")
  # LA HERRAMIENTA INTERNA ESTA EN EL TOP, LA EXTERNA EN EL BOTTOM
  # PERO TOP Y BOTTOM CONFUNDE POR LAS INDENTACIONES

  fi_x.write("/FUNCT/1000001\nmovx\n")    
  fi_y.write("/FUNCT/1000002\nmovy\n")      
  fi_z.write("/FUNCT/1000003\nmovz\n")    
  

  if (double_sided):
    fo_x.write("/FUNCT/1000004\nmovx\n")    
    fo_y.write("/FUNCT/1000005\nmovy\n")      
    fo_z.write("/FUNCT/1000006\nmovz\n")    
  
  t = 0.0
  
  z  = 0.0 
  # zo = -thck #ESTA HERRAMIENTA NO DESCIENDE (PARA EVITAR DEFORMACIONES IRREGULARES)
  # zi =  thck 
  zo  = zi = 0
  #p_S
  
  #ORIGINALLY ONLY INNER TOOL WAS DOWN
  # AS LIKE THIS; ASSUMING THAT is displaces at p_S
  #DOWNWARDS!
  #vz  = (thck + p_S + ball_gap -dz_up+dz) / t_ind # EN PRINCIPIO S EDESPLAZA SOLO LA INTERIOR  
  vz  = (p_S + ball_gap -dz_up+dz) / t_ind # EN PRINCIPIO S EDESPLAZA SOLO LA INTERIOR  
  vzo = (ball_gap +dz_up-dz)/ t_ind

  #-----------
  
  #INITIAL INNER TOOL POS:   zi_0 =  tool_rad + thck/2.0 + ball_gap + thck_rig
  #OUTER                     zo_0 = -tool_rad - thck/2.0 - ball_gap-thck_rig
  #SHOULD ACCOMPLISH THE FOLLOWING:
  #   INNER TOOL TIP - THICKNESS + ps_S = OUTER TOOL TIP
  #
  #Initial distance between tools
  #Both tools travel incremental depth dz 
  dist_0    = zi_0 - zo_0 
  #travel from #zi_0 position to zo_0
  dist_end  = abs(2.0 * tool_rad - thck + p_S )
  
  print ("-------------------------------------------------------")
  print ("Initial tool distance: ", dist_0 - 2*tool_rad)  
  print ("DISTANCE TO CONTACT BETWEEN TOOLS : Thck + 2 x (gap + tool_thck): ", thck + 2.0 * (ball_gap + thck_rig))  
  print ("End     tool distance: ", dist_end)

  z_move = abs( dist_end - dist_0)
  print ("Tool narrowing (S-thick): ", abs(p_S - thck))
  print ("Tool moving distance (discarding gap):", z_move - 2.0 * ball_gap)

  
  # if (double_sided):
    # zi_end    = zi_0 - z_move/2.0 - ball_gap - dz
    # zo_end    = zo_0 + z_move/2.0 + ball_gap - dz
  # else:
    # zi_end = zi_0 - ball_gap; #Only this tool
    
  #   INNER TOOL TIP - THICKNESS + ps_S = OUTER TOOL TIP
  #
  # if (double_sided):
    # vz  = (zi_end - zi_0)/t_ind
    # vzo = (zo_end - zo_0)/t_ind
  # else:

  
  # print ("Movement of inner tool: ", (zi_end - zi_0))
  # print ("Movement of outer tool: ", (zo_end - zo_0))
  # print ("Calculated ending toolpos zi %.3e , zo %.3e \n" %(zi_end-zi_0,zo_end-zo_0))
    
  #####################INDENTACION ######################### 
  xi = r0 - p_D/2.0
  xo = r0 + p_D/2.0

  # if (move_tool_to_inipos):
    # xo -= x_init
    # xi -= x_init
  f_test.write("X, Y, Z\n")
  
  
  while (t < t_ind):    


    zi -= vz  * dtind
    zo += vzo * dtind 
    
    #HAY QUE VER SI ES NECESARIO ESCRIBIR X E Y PARA TODOS LOS TIEMPOS
    fi_x.write(writeFloatField(t,20,6) + writeFloatField(xi,20,6) + "\n")
    fi_y.write(writeFloatField(t,20,6) + writeFloatField(0.,20,6) + "\n")
    fi_z.write(writeFloatField(t,20,6) + writeFloatField(zi,20,6) + "\n")
    
    f_test.write(str(xi) + ", " +str(0) + "," + str(zi) + "\n")
    
    if (double_sided):
      fo_x.write(writeFloatField(t,20,6) + writeFloatField(xo,20,6) + "\n")
      fo_y.write(writeFloatField(t,20,6) + writeFloatField(0.,20,6) + "\n")
      fo_z.write(writeFloatField(t,20,6) + writeFloatField(zo,20,6) + "\n")
    

    t +=dtind 
  print ("-------------------------------------")
  print ("Indentation ends: ")
  print ("Initial zi %.3e , zo %.3e \n" %(zi,zo))
  
  
  r = r0
  turn = 1
  ec = model.part[0].mesh[0].elem_count
  zt = (zi + zo)/2.0 # Z TEST IS USED BECAUSE ON ASDIF Z IS NOT MOVING
  r, t, zi, zo, zt = make_init_curve(r_ac1, 20.0, r,t, zi, zo, tool_speed, dz, da, zt, ec, is_ASDIF)

  print ("BEGINING CONE PART ----\n")
  print ("Time: ", t)
  print ("Initial radius ", r)

  r, t, zi, zo, zt = make_line(20.0, 0.003, r, t, turn, zi, zo, tool_speed, dz, da, zt, ec, is_ASDIF)
  print ("BEGINING RADIUS PART ----\n")
  print ("Time: ", t)
  print ("Initial radius ", r) 
  #-------------------------------------angout  angin
  r, t, zi, zo, zt = make_outer_curve(r_ac2, 50.0,  20.0, r,t, zi, zo, tool_speed, dz, da, zt, ec, is_ASDIF)  
  print("MAKING 20 deg line ")
  print ("Time: ", t)
  ### make_line(angle, depth, r, t, turn, zi, zo)
  r, t, zi, zo,zt = make_line(50.0, 0.013, r, t, turn, zi, zo, tool_speed, dz, da, zt, ec, is_ASDIF)  
  print ("MAKING END CURVE")
  r, t, zi, zo,zt = make_end_curve(r_ac3, 50.0, r, t, zi, zo, tool_speed, dz, da, zt, ec, is_ASDIF)


  dist = 10.0*tool_rad
  dt = dist / tool_speed
  print ("TOOL RETIREMENT TIME ", dt)
  t +=dt
  zi += dist
  zo -= dist
  
  # #TOOL RETIREMENT
  # fi_x.write(writeFloatField(t,20,6) + writeFloatField(xi,20,6) + "\n")
  # fi_y.write(writeFloatField(t,20,6) + writeFloatField(0.,20,6) + "\n")
  # fi_z.write(writeFloatField(t,20,6) + writeFloatField(zi,20,6) + "\n")
  
  # f_test.write(str(xi) + ", " +str(0) + "," + str(zi) + "\n")
  
  # if (double_sided):
    # fo_x.write(writeFloatField(t,20,6) + writeFloatField(xo,20,6) + "\n")
    # fo_y.write(writeFloatField(t,20,6) + writeFloatField(0.,20,6) + "\n")
    # fo_z.write(writeFloatField(t,20,6) + writeFloatField(zo,20,6) + "\n")
  
  #END TIME 
  if (calc_path):
    end_time = t

  print ("------- END PROCESS TIME (before release): ", t, "SECONDS")  
  print ("Overall Radius: ", xi)
  print ("Overall Depth: " , zt)
  model.end_proc_time = end_time


  #SPRINGBACK
  fi_x.close;fi_y.close;fi_z.close
  if (double_sided):
    fo_x.close;fo_y.close;fo_z.close


else: #NO PATH CALCULATION
  print ("Writing heat source functions")  
  prev_elem = -1
  print("Calculating heat source")
  
  if (thermal): 
    file = open(topfname)
    reader = csv.reader(file)
    data = list(csv.reader(file, delimiter=','))
    i = 1
    print ("Path size ", len(data))
    #while (i < len(data)):
    for e in range(model.part[0].mesh[0].elem_count):
      model.load_fnc[e].Append(t_interf,0.0)
    t = t_interf
    while (i < 100):
      if (i%100==0):
        print("Time  " +str(i) + " of " +str(len(data)))
      xi = np.array([float(data[i][0]), float(data[i][1]), 0.0])      
      e = model.part[0].mesh[0].findNearestElem(xi[0],xi[1],0.0)
      flog.write ("TIME %f, pos: %.6e %.6e, Found %d\n" % (t, xi[0], xi[1], e ))
      coord = str (model.part[0].mesh[0].elcenter[e].components)
      flog.write ("baricenter: %s\n" %(coord)) 
      prev_elem = e
      t+=dt
      model.load_fnc[e].Append(t,1.0e6)
      if (e != prev_elem):
        model.load_fnc[prev_elem].Append(t,0.0)  
      
      i += 1
      

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
  
print ("Writing input")
model.printRadioss("test")

model.printEngine(1, end_time,dtout,dtout_his)
if (mech):
  model.printRelease(2, end_time+supp_rel_time,dtout,dtout_his)
  model.printDynRelax(3,end_time+supp_rel_time+dynrel_time,dtout,dtout_his)


#---------------------------------------------------------------
#th_solid_model.printRadioss("solid")

# #Si no se coloca lambda no funciona
# b = Button(window, text="Generate", width=10, command=lambda:save(linea_g))
# b.grid(column=3, row=10)
# #b.pack()s

# window.title('Incremental Forming PATH Script')
# window.geometry("400x200+10+10")
# window.mainloop()
