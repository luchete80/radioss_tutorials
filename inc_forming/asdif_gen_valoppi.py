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
largo = 0.1
delta = 0.002
thck  = 5.0e-4      #Plate Thickness
thck_rig = 1.0e-4   #BALL
thck_supp = 1.0e-3  #SUPP

vscal_fac     = 2000.0 #Affects All magnitudes with s^-1: Tool Speed, HEAT CONDUCTIVIY, CONVECTION

#TOOL 
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
dz_up         = 5.0e-4
dz            = 1.0e-4    
dtind         = 0.01/vscal_fac    #Indentation time for crve generation
#!!!_ IMPORTANT THIS CAN BE enlarged if not thermal
da            = 1.0 #ANGLE FOR delta t in process. 
calc_path           = True
move_tool_to_inipos = True # THIS IS CONVENIENT, OTHERWISE RADIOSS THROWS ERROR DUE TO LARGE DISP TO INITIAL POS
ball_gap      = 1.0e-4  #THIS IS ASSIGNED SINCE IF NOT THE BALL INITIAL MOVEMENT DRAGS THE PLATE
r0            = 0.005

#dang           = 5.0  #Angle (deg) increment for path gen
p_D           = 2.5e-3     #ASDIF RADIAL DISTANCE BETWEEN TOOLS
p_S           = 4.3e-4     #ASDIF HEIGHT DISTANCE BETWEEN TOOLS

tool_rad      = 0.0025    #Tool radius
gap_cont      = -2.0e-4
dtout         = 5.0e-4
### --- ONLY USED WHEN NOT GENERATING PATH !!!
end_time      = 2.1879884613e+00
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
thermal             = False
cont_support        = True       #TRUE: SUPPORT IS MODELED BY CONTACT, FALSE: SUPPORT IS MODELED BY BCS ON NODES
double_sided        = True
manual_mass_scal    = False


#FROM XIAN 
# Optimization on the Johnson-Cook parameters of
# Ti-6Al-4V used for high speed cutting simulation
###### MATERIAL
mat = Material(1,thermal) #ID, THERMAL
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

fi_x = open("movi_x.inc","w")
fi_y = open("movi_y.inc","w")
fi_z = open("movi_z.inc","w")

f_test = open("tool_i.csv","w")

 
fo_x = open("movo_x.inc","w")
fo_y = open("movo_y.inc","w")
fo_z = open("movo_z.inc","w")


#CHANGE r, t 
def make_init_curve(rac, ang_1, r, t, zi, zo, ts, dz, dt, zt, ecount, asdif): #Convex radius is from outside
  heat_on_prev= np.full(ecount, False)
  heat_on     = np.full(ecount, False)
  
  rinc = 0
  turn = 1
  ######################## VUELTAS ##############################
  end_angle = ang_1 *np.pi / 180.0
  end = False

  while (not end):
  
  
    t_ang = 2.0 * pi * r / ts #Tiempo (incremento) de cada vuelta (ASUMIENDO RADIO CONSTANTE)
    print("Turn %d Turn Time %.3e Time %.3e Radius %.3e\n" %(turn, t_ang,t,r))
    t_vuelta = t + t_ang  #Tiempo de final de vuelta (TOTAL)
    t_0 = t               #Tiempo de comienzo de vuelta
    t_inc = 0.0           # t - t_0

    vz = dz / t_ang       #ORIGINAL, CONSTANT
    
    
    #- 
    #  \
    # a |
    # GIving an angle

    #Calculate angle

    ang = np.arccos((rac-turn*dz)/rac)
    dr  = (rac-turn*dz) * np.tan(ang) - rinc

      
    print("Angle ",ang*180.0/np.pi, "deg, dr ", dr)
    print ("Initial turn radius ",r - p_D/2.0 - rinc )
    dt = t_ang * (np.pi /180.0 * da ) / (2.0*np.pi)

    while (t < t_vuelta): #VUELTAS  
      # print ("t_inc %.3e t_ang %.3e"%(t_inc,t_ang))
      if (not asdif):
        ri_curr = r - p_D/2.0 - dr * t_inc/t_ang
        ro_curr = r + p_D/2.0 - dr * t_inc/t_ang
      else:
        ri_curr = r - p_D/2.0 + dr * t_inc/t_ang
        ro_curr = r + p_D/2.0 + dr * t_inc/t_ang
      
      # ri_curr = r - p_D/2.0 - dr * t_inc/t_ang
      # print ("rcurr, z, " + str(ri_curr) + str (zi))
      xi = ri_curr * cos(2.0*pi*t_inc/t_ang)
      yi = ri_curr * sin(2.0*pi*t_inc/t_ang)

      if (not asdif):
        zi -= vz * dt
        zo -= vz * dt
        zt -= vz * dt        
      else:
        zt += vz * dt
        
      xo = ro_curr*cos(2.0*pi*t_inc/t_ang)
      yo = ro_curr *sin(2.0*pi*t_inc/t_ang)      
      
      f_test.write(str(xi) + ", " +str(yi) + "," + str(zt) + "\n")
      
      fi_x.write(writeFloatField(t,20,6) + writeFloatField(xi,20,6) + "\n")
      fi_y.write(writeFloatField(t,20,6) + writeFloatField(yi,20,6) + "\n")
      fi_z.write(writeFloatField(t,20,6) + writeFloatField(zi,20,6) + "\n")
      if (double_sided):
        fo_x.write(writeFloatField(t,20,6) + writeFloatField(xo,20,6) + "\n")
        fo_y.write(writeFloatField(t,20,6) + writeFloatField(yo,20,6) + "\n")
        fo_z.write(writeFloatField(t,20,6) + writeFloatField(zo,20,6) + "\n")
      
      
      t_inc +=dt
      t += dt
      heat_on[:] = False
      if (thermal):
        e = model.part[0].mesh[0].findNearestElem(xi,yi,zi)
        heat_on[e] = True
        # print ("ELEMENT ", e , "found" )
        # print ("heat is ", heat_on_prev[e])
        if (not (heat_on_prev[e])):
          flog.write ("TIME %f, pos: %.6e %.6e, Found %d\n" % (t, xi, yi, e ))
          coord = str (model.part[0].mesh[0].elcenter[e].components)
          flog.write ("baricenter: %s\n" %(coord))  
          model.load_fnc[e].Append(t,1.0e6)
          
          
              # for i in range (self.mesh[0].elem_count):
      # line = writeIntField(i + self.mesh[0].ini_elem_id ,10)
      # for d in range (4):
        # # print (self.mesh[0].ini_node_id, ", ")
        # line = line + writeIntField(self.mesh[0].elnod[i][d] 
         
      for e in range(ecount):
        if (not heat_on[e] and heat_on_prev[e]):
          model.load_fnc[e].Append(t,0.0)       
      
      heat_on_prev[:] = heat_on[:]
      
    rinc+=dr
    if (asdif):
      r += dr
    else:
      r -=dr
    turn += 1    


    if (ang > end_angle):
      end = True
  return r,t,zi,zo, zt


# NOT VERIFIED FOR SPIF
# IE OUT TO IN
#Alpha dimninisesh to zero
def make_end_curve(rac, ang_1, r, t, zi, zo, ts, dz, dt, zt, ecount, asdif): #Convex radius is from outside
  heat_on_prev= np.full(ecount, False)
  heat_on     = np.full(ecount, False)
  
  rinc = 0
  turn = 1
  ######################## VUELTAS ##############################
  end_angle = 0.0
  end = False

  rini = np.sin(ang_1 *np.pi / 180.0)*rac
  zini = np.cos(ang_1 *np.pi / 180.0)*rac
  while (not end):
  
  
    t_ang = 2.0 * pi * r / ts #Tiempo (incremento) de cada vuelta (ASUMIENDO RADIO CONSTANTE)
    print("Turn %d Turn Time %.3e Time %.3e Radius %.3e\n" %(turn, t_ang,t,r))
    t_vuelta = t + t_ang  #Tiempo de final de vuelta (TOTAL)
    t_0 = t               #Tiempo de comienzo de vuelta
    t_inc = 0.0           # t - t_0

    vz = dz / t_ang       #ORIGINAL, CONSTANT
    
    #+----> ASDIF
    # - -------
    #     /
    #    /
    # a |
    # GIving an angle

    #Calculate angle
    if (zini+turn*dz < rac):
      ang = np.arccos((zini+turn*dz)/rac)
      dr  = rini - rinc - (zini+turn*dz)*np.tan(ang) 
      
      print ("rini ", rini, "rinc", rinc)
        
      print("Angle ",ang*180.0/np.pi, "deg, dr ", dr)
      print ("Initial turn radius ",r - p_D/2.0 - rinc )
      print ("zini+turn*dz", zini+turn*dz, "rac", rac)
      
      dt = t_ang * (np.pi /180.0 * da ) / (2.0*np.pi)
      if (zini+turn*dz < rac):

        while (t < t_vuelta): #VUELTAS  
          # print ("t_inc %.3e t_ang %.3e"%(t_inc,t_ang))
          if (not asdif):
            ri_curr = r - p_D/2.0 - dr * t_inc/t_ang
            ro_curr = r + p_D/2.0 - dr * t_inc/t_ang
          else:
            ri_curr = r - p_D/2.0 + dr * t_inc/t_ang
            ro_curr = r + p_D/2.0 + dr * t_inc/t_ang
          
          # ri_curr = r - p_D/2.0 - dr * t_inc/t_ang
          # print ("rcurr, z, " + str(ri_curr) + str (zi))
          xi = ri_curr * cos(2.0*pi*t_inc/t_ang)
          yi = ri_curr * sin(2.0*pi*t_inc/t_ang)

          if (not asdif):
            zi -= vz * dt
            zo -= vz * dt
            zt -= vz * dt        
          else:
            zt += vz * dt
            
          xo = ro_curr*cos(2.0*pi*t_inc/t_ang)
          yo = ro_curr *sin(2.0*pi*t_inc/t_ang)      
          
          f_test.write(str(xi) + ", " +str(yi) + "," + str(zt) + "\n")
          
          fi_x.write(writeFloatField(t,20,6) + writeFloatField(xi,20,6) + "\n")
          fi_y.write(writeFloatField(t,20,6) + writeFloatField(yi,20,6) + "\n")
          fi_z.write(writeFloatField(t,20,6) + writeFloatField(zi,20,6) + "\n")
          if (double_sided):
            fo_x.write(writeFloatField(t,20,6) + writeFloatField(xo,20,6) + "\n")
            fo_y.write(writeFloatField(t,20,6) + writeFloatField(yo,20,6) + "\n")
            fo_z.write(writeFloatField(t,20,6) + writeFloatField(zo,20,6) + "\n")
          
          
          t_inc +=dt
          t += dt
          heat_on[:] = False
          if (thermal):
            e = model.part[0].mesh[0].findNearestElem(xi,yi,zi)
            heat_on[e] = True
            # print ("ELEMENT ", e , "found" )
            # print ("heat is ", heat_on_prev[e])
            if (not (heat_on_prev[e])):
              flog.write ("TIME %f, pos: %.6e %.6e, Found %d\n" % (t, xi, yi, e ))
              coord = str (model.part[0].mesh[0].elcenter[e].components)
              flog.write ("baricenter: %s\n" %(coord))  
              model.load_fnc[e].Append(t,1.0e6)
              
              
                  # for i in range (self.mesh[0].elem_count):
          # line = writeIntField(i + self.mesh[0].ini_elem_id ,10)
          # for d in range (4):
            # # print (self.mesh[0].ini_node_id, ", ")
            # line = line + writeIntField(self.mesh[0].elnod[i][d] 
             
          for e in range(ecount):
            if (not heat_on[e] and heat_on_prev[e]):
              model.load_fnc[e].Append(t,0.0)       
          
          heat_on_prev[:] = heat_on[:]
          
        rinc+=dr
        if (asdif):
          r += dr
        else:
          r -=dr
        turn += 1    
    
    else:
      end =True

  return r,t,zi,zo, zt



#
#Both angles are from the outside and respect oto horizontal 
#   \
#    \
# beta\
#------------ >> WORKPIECE SHAPE

# ANGLES IN DEGs
# Beta is angle w/hor line
# FOR SPIF
#ALWAYS beta 0 is outside (LARGER) angle
def make_outer_curve(rac, beta0, beta1, r, t, zi, zo, ts, dz, dt, zt, ecount, asdif): #Convex radius is from outside
  heat_on_prev= np.full(ecount, False)
  heat_on     = np.full(ecount, False)
  rinc = 0.0
  turn = 1
  ######################## VUELTAS ##############################

    #ALPHA in incrementing and beta (PI/2 - alpha)
    # is decrementing
    #   |
    #   |alpha /
    #    \    /
    #     \  
    # beta \ 
    #       ------- <<--- Workpiece curve
    #      b1
    # GIving an angle
  #SPIF from 0 -> 1, alpha increasing
  #ASDIF from 1->0
  alpha0 = np.pi/2.0 - beta0 * np.pi /180.0
  alpha1 = np.pi/2.0 - beta1 * np.pi /180.0
  #USED FOR ASDIF VERSION------------------
  #----------------------------------------
  rini = rac * np.cos(alpha1)
  zini = rac * np.sin(alpha1)

  racc = rac * (1.0 - np.cos(alpha0))
  zacc  = rac * np.sin(alpha0)  #SUPPOSED INITIAL DEPTH TO REACH INITIAL APHA
  print ("Alpha0, Acc z ", alpha0, zacc)
  
  end = False

  while (not end):
  
  
    t_ang = 2.0 * pi * r / ts #Tiempo (incremento) de cada vuelta (ASUMIENDO RADIO CONSTANTE)
    print("Turn %d Turn Time %.3e Time %.3e Radius %.3e\n" %(turn, t_ang,t,r))
    t_vuelta = t + t_ang  #Tiempo de final de vuelta (TOTAL)
    t_0 = t               #Tiempo de comienzo de vuelta
    t_inc = 0.0           # t - t_0

    vz = dz / t_ang       #ORIGINAL, CONSTANT

    if (asdif):  
      ztest = zi    
    
    #INITIAL VALUES
    z_0i = zi
    z_0o = zo
    z_c = (zi + zo)/2.0 - rac
    print ("zi ", zi)
    
    if (not asdif):
      alpha = np.arcsin((zacc+turn*dz)/rac)
      dr    = rac - ((zacc+turn*dz) / np.tan(alpha))  - rinc - racc
    else:
      alpha = np.arcsin((zini-turn*dz)/rac)
      dr    = ((zini-turn*dz)/np.tan(alpha)) - rini - rinc
      
    
    print("Aim angle ",alpha*180.0/np.pi, "deg, dr ", dr)
    # print ("Initial turn radius ",r - p_D/2.0 - rinc )
    dt = t_ang * (np.pi / 180.0 * da ) / (2.0*np.pi)
    while (t < t_vuelta): #VUELTAS  
      # print ("t_inc %.3e t_ang %.3e"%(t_inc,t_ang))
      if (not asdif):
        ri_curr = r - p_D/2.0 - dr * t_inc/t_ang
        ro_curr = r + p_D/2.0 - dr * t_inc/t_ang
      else:
        ri_curr = r - p_D/2.0 + dr * t_inc/t_ang
        ro_curr = r + p_D/2.0 + dr * t_inc/t_ang
      # print ("rcurr, z, " + str(ri_curr) + str (zi))
      xi = ri_curr * cos(2.0*pi*t_inc/t_ang)
      yi = ri_curr * sin(2.0*pi*t_inc/t_ang)

      if (not asdif):
        zi -= vz * dt
        zo -= vz * dt     
        zt -= vz * dt
      else:
        zt += vz * dt
        
      xo = ro_curr * cos(2.0*pi*t_inc/t_ang)
      yo = ro_curr * sin(2.0*pi*t_inc/t_ang)      
      
      
      f_test.write(str(xi) + ", " +str(yi) + "," + str(zt) + "\n")
      
      fi_x.write(writeFloatField(t,20,6) + writeFloatField(xi,20,6) + "\n")
      fi_y.write(writeFloatField(t,20,6) + writeFloatField(yi,20,6) + "\n")
      fi_z.write(writeFloatField(t,20,6) + writeFloatField(zi,20,6) + "\n")
      if (double_sided):
        fo_x.write(writeFloatField(t,20,6) + writeFloatField(xo,20,6) + "\n")
        fo_y.write(writeFloatField(t,20,6) + writeFloatField(yo,20,6) + "\n")
        fo_z.write(writeFloatField(t,20,6) + writeFloatField(zo,20,6) + "\n")
      
      
      t_inc +=dt
      t += dt

      heat_on[:] = False
      if (thermal):
        e = model.part[0].mesh[0].findNearestElem(xi,yi,zi)
        heat_on[e] = True
        # print ("ELEMENT ", e , "found" )
        # print ("heat is ", heat_on_prev[e])
        if (not (heat_on_prev[e])):
          flog.write ("TIME %f, pos: %.6e %.6e, Found %d\n" % (t, xi, yi, e ))
          coord = str (model.part[0].mesh[0].elcenter[e].components)
          flog.write ("baricenter: %s\n" %(coord))  
          model.load_fnc[e].Append(t,1.0e6)
         
      for e in range(ecount):
        if (not heat_on[e] and heat_on_prev[e]):
          model.load_fnc[e].Append(t,0.0)       
      
      heat_on_prev[:] = heat_on[:]

      if (thermal):
        e = model.part[0].mesh[0].findNearestElem(xi,yi,zi)
        flog.write ("TIME %f, pos: %.6e %.6e, Found %d\n" % (t, xi, yi, e ))
        coord = str (model.part[0].mesh[0].elcenter[e].components)
        flog.write ("baricenter: %s\n" %(coord))  
        model.load_fnc[e].Append(t,1.0e6)
      
    rinc+=dr
    if (asdif):
      if (alpha < alpha0):
        end = True
      r += dr
    else:
      if (alpha > alpha1):
        end = True
      r -=dr
    turn += 1    



  return r,t,zi,zo, zt 
  
#Make a cone 
def make_line(angle, depth, r, t, turn, zi, zo, ts, dz, dt, zt, ecount, asdif):
  heat_on_prev= np.full(ecount, False)
  heat_on     = np.full(ecount, False)
  ######################## VUELTAS ##############################
  end = False
  if (asdif):
    rlim = r + depth / np.tan(angle * np.pi / 180.0)
  else:
    rlim = r - depth / np.tan(angle * np.pi / 180.0)

  if (rlim<0):
    print ("ERROR, min line is negative, check depth/angle ratio")
  print ("Line (cone) limit radius  ", rlim)
  
  while ( not end):
    print ("r, ts ", r, ts)
    t_ang = 2.0 * np.pi * r / ts #Tiempo (incremento) de cada vuelta (ASUMIENDO RADIO CONSTANTE)
    print("Turn %d Turn Time %.3e Time %.3e Radius %.3e\n" %(turn, t_ang,t,r))
    t_vuelta = t + t_ang  #Tiempo de final de vuelta (TOTAL)
    t_0 = t               #Tiempo de comienzo de vuelta
    t_inc = 0.0           # t - t_0
    vz = dz / t_ang
    dr = dz / np.tan(angle * np.pi / 180.0)
    dt = t_ang * (np.pi / 180.0 * da ) / (2.0*np.pi)
    while (t < t_vuelta): #VUELTAS  
      # print ("t_inc %.3e t_ang %.3e"%(t_inc,t_ang))

      if (not asdif):
        ri_curr = r - p_D/2.0 - dr * t_inc/t_ang
        ro_curr = r + p_D/2.0 - dr * t_inc/t_ang
      else:
        ri_curr = r - p_D/2.0 + dr * t_inc/t_ang
        ro_curr = r + p_D/2.0 + dr * t_inc/t_ang
      
      xi = ri_curr *cos(2.0*pi*t_inc/t_ang)
      yi = ri_curr *sin(2.0*pi*t_inc/t_ang)


      xo = ro_curr *cos(2.0*pi*t_inc/t_ang)
      yo = ro_curr *sin(2.0*pi*t_inc/t_ang)      


      if (not asdif):
        zi -= vz * dt
        zo -= vz * dt     
        zt -= vz * dt
      else:
        zt += vz * dt
        # #ONLY! IF YOU WANT TO TEST SHAPE, TOOL IS IN PLANE
        # zi += vz * dt
        # zo += vz * dt     

      f_test.write(str(xi) + ", " +str(yi) + "," + str(zt) + "\n")
      
      # print("zi %.3e , zo %.3e \n" %(zi,zo))
      # z -= t_inc/t_ang * dr # CAMBIAR A dz
      
      fi_x.write(writeFloatField(t,20,6) + writeFloatField(xi,20,6) + "\n")
      fi_y.write(writeFloatField(t,20,6) + writeFloatField(yi,20,6) + "\n")
      fi_z.write(writeFloatField(t,20,6) + writeFloatField(zi,20,6) + "\n")
      if (double_sided):
        fo_x.write(writeFloatField(t,20,6) + writeFloatField(xo,20,6) + "\n")
        fo_y.write(writeFloatField(t,20,6) + writeFloatField(yo,20,6) + "\n")
        fo_z.write(writeFloatField(t,20,6) + writeFloatField(zo,20,6) + "\n")
     
      
      t_inc +=dt
      t += dt

      heat_on[:] = False
      if (thermal):
        e = model.part[0].mesh[0].findNearestElem(xi,yi,zi)
        heat_on[e] = True
        # print ("ELEMENT ", e , "found" )
        # print ("heat is ", heat_on_prev[e])
        if (not (heat_on_prev[e])):
          flog.write ("TIME %f, pos: %.6e %.6e, Found %d\n" % (t, xi, yi, e ))
          coord = str (model.part[0].mesh[0].elcenter[e].components)
          flog.write ("baricenter: %s\n" %(coord))  
          model.load_fnc[e].Append(t,1.0e6)
         
      for e in range(ecount):
        if (not heat_on[e] and heat_on_prev[e]):
          model.load_fnc[e].Append(t,0.0)       
      
      heat_on_prev[:] = heat_on[:]

      if (thermal):
        e = model.part[0].mesh[0].findNearestElem(xi,yi,zi)
        flog.write ("TIME %f, pos: %.6e %.6e, Found %d\n" % (t, xi, yi, e ))
        coord = str (model.part[0].mesh[0].elcenter[e].components)
        flog.write ("baricenter: %s\n" %(coord))  
        model.load_fnc[e].Append(t,1.0e6)
      
    if (asdif):
      r += dr
      if (r >= rlim):
        end = True
    else:
      r -=dr
      if (r <= rlim):
        end = True
    turn += 1  
    


  return r,t,zi,zo, zt

supp_mesh = []
supp_part = []

shell_elnod = [(1,2,3,4)]


shell_mesh = Plane_Mesh(1,largo,delta)

solid_mesh = Rect_Solid_Mesh(1,largo,largo,thck,delta,delta,thck)
#(self, id, radius, ox,oy,oz, divisions):
zi_0 = tool_rad + thck/2.0 + ball_gap + thck_rig
sph1_mesh = Sphere_Mesh(2, tool_rad-thck_rig/2.0,        \
                        0.0, 0.0,zi_0, \
                                        5) #(id, radius, divisions):
zo_0 = -tool_rad - thck/2.0 - ball_gap-thck_rig
if (double_sided):
  sph2_mesh = Sphere_Mesh(3, tool_rad-thck_rig/2.0,        \
                        0.0, 0.0,zo_0, \
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

# THERMAL SOLID MODEL --------------------------------------------------------
th_solid_model = ThermalSolidModel()
solid_pt =Part(1)
solid_pt.AppendMesh(solid_mesh)

th_solid_model.AppendPart(solid_pt)
th_solid_model.AppendMat(mat)

if (calc_path):
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
  # vz  = (thck + p_S + ball_gap +dz) / t_ind # EN PRINCIPIO S EDESPLAZA SOLO LA INTERIOR  
  # vzo = (ball_gap -dz)/ t_ind

  vz  = (thck + p_S + ball_gap -dz_up) / t_ind # EN PRINCIPIO S EDESPLAZA SOLO LA INTERIOR  
  vzo = (ball_gap +dz_up)/ t_ind
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


#---------------------------------------------------------------
th_solid_model.printRadioss("solid")

# #Si no se coloca lambda no funciona
# b = Button(window, text="Generate", width=10, command=lambda:save(linea_g))
# b.grid(column=3, row=10)
# #b.pack()s

# window.title('Incremental Forming PATH Script')
# window.geometry("400x200+10+10")
# window.mainloop()
