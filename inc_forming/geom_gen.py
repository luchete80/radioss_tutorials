
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
