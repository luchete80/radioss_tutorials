from math import *
import numpy as np

debug = True

def writeFloatField(number, length, decimals):
  fmt ='%.' + str(decimals) + 'e'
  # print ('format ' + fmt)
  s = fmt % number
  spaces = ''
  for i in range ((int)(length - len(s))):
    spaces = spaces + ' '
  output = spaces + s
  # print (spaces + s)
  return output

def writeIntField(number, length):
  s = '%d' % number
  spaces = ''
  for i in range ((int)(length - len(s))):
    spaces = spaces + ' '
  output = spaces + s
  # print (spaces + s)
  return output

def Norm2(v):
  norm = 0.0
  if isinstance(v, Vector):
    for i in range (len(v.components)):
      norm = norm + v.components[i] * v.components[i]
  return norm
      
class Vector:
  def __init__(self, *components):
      self.components = components
  def __mul__(self, other):
    components = []
    if isinstance(other, Vector):
      # if (len(self.components)!=len(other.components)):
        # print ("Different length size")
      for i in range (len(self.components)):
        components.append(self.components[i] * other.components[i])
    else:
      components = (other * x for x in self.components)
    return Vector(*components)
  # addition is normally a binary operation between self and other object
  # def __add__(self, other):
    # if isinstance(other, Vector):
      # new_vec = Vector()
      # new_vec.X = self.X + other.X
      # new_vec.Y = self.X + other.Y
      # return new_vec
    # else:
      # raise TypeError("value must be a vector.")
  # def __add__(self, other):
    # added =[]
    # for i in range(len(self.components)):
      # #added = tuple( a + b for a, b in zip(self, other) )
      # added.append(self.components[i] + other.components[i])
      # return Vector(*added)
  def __add__(self, other):
    if isinstance(other, Vector):
    # other.args is the correct analog of self.args
      a = [arg1 + arg2 for arg1, arg2 in zip(self.components, other.components)]
    return self.__class__(*a)
  def __sub__(self, other):
    if isinstance(other, Vector):
    # other.args is the correct analog of self.args
      a = [arg1 - arg2 for arg1, arg2 in zip(self.components, other.components)]
    return self.__class__(*a)
  def Norm():
    norm = 0.0
    norm = [norm + arg1 for arg1 in self.components]
    norm = sqrt (norm)
    return norm
    
  def __repr__(self):
      return str(self.components)
      
  # # __repr__ and __str__ must return string
  # def __repr__(self):
    # # return str(self.components)
    # # return f"Vector{self.components}"
    # return str(self.components)

  def __str__(self):
    # return str(self.components)
    return "Vector{self.components}"
    # return str(self.components)
    
# def __add__(self, other):
  # if isinstance(other, Vector):
    # new_vec = Vector()
    # new_vec.X = self.X + other.X
    # new_vec.Y = self.X + other.Y
    # return new_vec
  # else:
    # raise TypeError("value must be a vector.")

#TODO: CHANGE ALL TO NODE
class Node(Vector):
  def __init__(self, id, *components):
    self.components = components
    self.id = id
    
    
###############################################################################
#TODO: DEFINE MESH
class Mesh:
  node_count = (int) (0.0)
  elem_count = (int) (0.0)
  print_segments = False
  nodes = []
  elnod = []
  elcenter = []
  ini_node_id = 1
  ini_elem_id = 1
  id = 0
  type = "shell"
  # elnod = [(1,2,3,4)]
  def __init__(self, largo, delta):
    elem_xy = largo/delta
    self.node_count = (int)(elem_xy)
      # self.r = realpart
      # self.i = imagpart
  def __init__(self):
    self.data = []
    
  def alloc_nodes(nod_count):
    for i in range (nod_count-1):
      nodes.append((0.,0.,0.))

  def add_node(self,x,y,z):
    self.nodes.append((x,y,z))
    self.node_count += 1
  
  def printESurfsRadioss(self,f):
    if (self.print_segments):
      for i in range (self.elem_count):
        line = "/SURF/SEG/%d\nSURF_SEG_%d\n" % (i+1,i+1)
        f.write(line)
        line = writeIntField(i+1,10)
        for d in range (4):
          line = line + writeIntField(self.elnod[i][d]+1,10)
        f.write(line + '\n')
  def printRadioss(self,fname):
    f = open(fname,"w+")
    # self.writeFloatField(-100.0,20,6)
    f.write('/NODES\n')
    print("Printing nodes..\n")
    for i in range (self.node_count):
      line = writeIntField(i+1,10)
      for d in range (3):
        line = line + writeFloatField(self.nodes[i][d],20,6) 
      # f.write("%.6e, %.6e\n" % (self.nodes[i][0],self.nodes[i][1]))
      f.write(line + '\n')
    if (type=="shell"):
      f.write('/SHELL/' + str(self.id) + '\n')
    if (type=="solid"):
      f.write('/SOLID/' + str(self.id) + '\n')
    if (type=="spring"):
      f.write('/SPRING/' + str(self.id) + '\n')
    
    print("Printing elements..\n")
    for i in range (self.elem_count):
      line = writeIntField(i+1,10)
      for d in range (4):
        line = line + writeIntField(self.elnod[i][d]+1,10)
      f.write(line + '\n')
  def AddRigidNode(self,x,y,z):
    self.nodes.append((x,y,z))
    print ("Added  Rigid Node ", self.node_count)
    self.node_count = self.node_count + 1    
  
  def printContSurfRadioss(self,f): #ALREADY OPENED
    if(debug):
        print("/SURF/PART/%d\n"%(self.id+1000000))
    f.write("/SURF/PART/%d\n"%(self.id+1000000))
    f.write("PART_RIG_SURF_%d\n"%self.id)
    f.write(writeIntField(self.id,10)+"\n")

  #THIS IS ONLY USED FOR CONVECTION----------
  def printPartSurfRadioss(self,f): #ALREADY OPENED
    f.write("/SURF/PART/%d\n"%(self.id*1e6))
    f.write("PART_WORKPIECE_SURF_%d\n"%self.id)
    f.write(writeIntField(self.id,10)+"\n")
    
  def printRigidRadioss(self,f): #ALREADY OPENED
    #IF THE SURFACE IS RIGID; IT TAKES ITS LAST NODE
    f.write("/RBODY/%d\n"%(self.id*100))
    f.write("PART_%d\n"%(self.id))
    f.write("#---1----|----2----|----3----|----4----|----5----|----6----|----7----|----8----|----9----|---10----|\n");
    f.write("# node_ID    sens_ID	  Skew_ID	   Ispher	               Mass	  grnd_ID	    Ikrem	     ICoG	  surf_ID\n");
    line = writeIntField(self.ini_node_id + self.node_count - 1, 10) + "                                                  " #50 spaces
    line = line + writeIntField(self.id,10) + "\n"
    f.write(line)
    f.write("\n\n\n") # 3 more line needed for RBODY COMMAND

  def printConvRadioss(self,vs_fac,f):
    
    f.write("#---1----|----2----|----3----|----4----|----5----|----6----|----7----|----8----|----9----|---10----|\n")
    f.write("/UNIT/11\n")
    f.write("unit for convection load\n")
    f.write("                  kg                   m                   s\n")
    f.write("/CONVEC/1/11\n")
    f.write("convect with ambient air \n")
    f.write("#  SURF_ID    FCT_ID   SENS_ID\n")
    f.write(writeIntField(self.id*1e6,10)+"   1000000         0\n")
    f.write("#             ASCALE              FSCALE              TSTART               TSTOP                   H\n")
    f.write("                   0                   0                   0                   0" + writeFloatField(30.0*vs_fac,20,6) +"\n")
    f.write("#---1----|----2----|----3----|----4----|----5----|----6----|----7----|----8----|----9----|---10----|\n")
    f.write("/FUNCT/1000000\n")
    f.write("temperature of ambient air (with constant temperature 293K)\n")
    f.write("#                  X                   Y\n")
    f.write("                   0                 20\n")
    f.write("                   1                 20\n")
    f.write("#---1----|----2----|----3----|----4----|----5----|----6----|----7----|----8----|----9----|---10----|\n")
    f.write("#ENDDATA  \n")
  
  def getRigidNode(self): #ALREADY OPENED
    print (self.ini_node_id + self.node_count - 1)
    return self.ini_node_id + self.node_count - 1
  def writeCenters(self):
    print ("Writing centers ")
    # print ("self nodes size ",len(self.nodes))
    for e in range (self.elem_count):
      center = [0.,0.,0.]
      for n in range (4):
        for dim in range (3):
          # print ("elem ", e, " node ",n, "el node ", self.elnod[e][n])
          center[dim] = center[dim] + self.nodes[self.elnod[e][n]][dim]

      for dim in range (3):
        center[dim] = center[dim] / 4.0
      self.elcenter.append(Vector(center[0], center[1], center[2]))
    # for e in range (self.elem_count):
      # print ("Element centers ", self.elcenter[e])
        # elcenter
  def findNearestElem(self, x,y,z):
    mx = -1
    maxdist = 1000.0
    for e in range (self.elem_count):
      pos = Vector(x,y,z)
      dist = Norm2(pos - self.elcenter[e])
      # print ("dist: ", dist)
      if ( dist < maxdist ):
        maxdist = dist
        mx = e
    return mx

class Plane_Mesh(Mesh):
  ini_node_id = 1 
  ini_elem_id = 1
  nodes = []
  elnod = []
  elcenter = []
  def set_ini_nod_ele (inin, inie):
    ini_node_id = inin 
    ini_elem_id = inie
  def __init__(self, id, largo, delta):
    self.nodes = []
    self.elnod = []
    self.id = id
    elem_xy = (int)(largo/delta)
    nc = (int)(elem_xy+1)
    self.node_count = nc * nc
    self.elem_count = (int)((elem_xy)*(elem_xy))
    print ('Nodes Count: ' + str(self.node_count))
    print ('Elem Count: ' + str(self.node_count))
    y = -largo/2.0
    for j in range (nc):
      x = -largo/2.0
      for i in range (nc):
        self.nodes.append((x,y,0.))
        x = x + delta
      y = y + delta
      
    for ey in range (elem_xy):    
      for ex in range (elem_xy):   
        #THIS IS THE REAL NODE POSITION (FROM ZERO)
        #UPPER NORMAL IS CLOCKWISE
        self.elnod.append(((elem_xy+1)*ey+ex,(elem_xy+1)*ey + ex+1,(elem_xy+1)*(ey+1)+ex+1,(elem_xy+1)*(ey+1)+ex))
                    # elem%elnod(i,:)=[(nel(1)+1)*ey + ex+1,(nel(1)+1)*ey + ex+2,(nel(1)+1)*(ey+1)+ex+2,(nel(1)+1)*(ey+1)+ex+1]         
              # print *, "Element ", i , "Elnod", elem%elnod(i,:) 
    # print(self.elnod)
    self.writeCenters()


class Rect_Plane_Mesh(Mesh):
  ini_node_id = 1 
  ini_elem_id = 1
  nodes = []
  elnod = []
  elcenter = []
  z = 0.0
  def set_ini_nod_ele (inin, inie):
    ini_node_id = inin 
    ini_elem_id = inie
  def __init__(self, id, lx, ly, elem_x, elem_y, ox, oy, z_, flip):
    self.nodes = []
    self.elnod = []
    self.id = id
    dx = lx/elem_x
    print ("dx: ",dx)
    dy = ly/elem_y
    z = z_
    print ("Adding rect on z: ", z_)
    ncx = (int)(elem_x+1)
    ncy = (int)(elem_y+1)
    
    self.node_count = ncx * ncy
    self.elem_count = (int)((elem_x)*(elem_y))
    print ('Nodes Count: ' + str(self.node_count))
    print ('Elem Count: ' + str(self.node_count))
    y = oy
    for j in range (ncy):
      x = ox
      for i in range (ncx):
        self.nodes.append((x,y,z_))
        x = x + dx
        # print ('x y ', x, y)
      y = y + dy
      
    for ey in range (elem_y):    
      for ex in range (elem_x):   
        #THIS IS THE REAL NODE POSITION (FROM ZERO)
        if (not flip):
          #UPPER NORMAL IS CLOCKWISE
          self.elnod.append(((elem_x+1)*ey+ex,(elem_x+1)*ey + ex+1,(elem_x+1)*(ey+1)+ex+1,(elem_x+1)*(ey+1)+ex))
                    # elem%elnod(i,:)=[(nel(1)+1)*ey + ex+1,(nel(1)+1)*ey + ex+2,(nel(1)+1)*(ey+1)+ex+2,(nel(1)+1)*(ey+1)+ex+1]   
        else:
          self.elnod.append(((elem_x+1)*ey+ex+1,(elem_x+1)*ey + ex,(elem_x+1)*(ey+1)+ex,(elem_x+1)*(ey+1)+ex+1))
              # print *, "Element ", i , "Elnod", elem%elnod(i,:) 
    # print(self.elnod)
    self.writeCenters()

class Rect_Solid_Mesh(Mesh):
  ini_node_id = 1 
  ini_elem_id = 1
  nodes = []
  elnod = []
  elcenter = []
  z = 0.0
  type = "solid" #for writing
  def set_ini_nod_ele (inin, inie):
    ini_node_id = inin 
    ini_elem_id = inie
  def __init__(self, id, lx, ly, lz, dx, dy, dz, ox=0, oy=0, oz=0):
    self.nodes = []
    self.elnod = []
    self.id = id
    elem_x = int(lx/dx)
    print ("dx: ",dx)
    elem_y = int(ly/dy)
    elem_z = int(lz/dz)

    
    ncx = (int)(elem_x+1)
    ncy = (int)(elem_y+1)
    ncz = (int)(elem_z+1)
    
    self.node_count = ncx * ncy * ncz
    self.elem_count = (int)((elem_x)*(elem_y)*(elem_z))
    print ('Nodes Count: ' + str(self.node_count))
    print ('Elem Count: ' + str(self.node_count), elem_x,elem_y,elem_z)
    z = oz
    for k in range (ncz):
      y = oy
      for j in range (ncy):
        x = ox
        for i in range (ncx):
          self.nodes.append((x,y,z))
          x += dx 
          # print ('x y ', x, y)
        y += dy
      z += dz
          # int nb1 = nnodz*ez + (nel[0]+1)*ey + ex;
          # int nb2 = nnodz*ez + (nel[0]+1)*(ey+1) + ex;
          
          # elnod_h[ei  ] = nb1;                      nodel_count_h[nb1  ] ++;          
          # elnod_h[ei+1] = nb1+1;                    nodel_count_h[nb1+1] ++;
          # elnod_h[ei+2] = nb2+1;                    nodel_count_h[nb2+1] ++;
          # elnod_h[ei+3] = nb2;                      nodel_count_h[nb2  ] ++;
          
          # elnod_h[ei+4] = nb1 + nnodz*(ez+1);       nodel_count_h[nb1 + nnodz*(ez+1)    ]++;   
          # elnod_h[ei+5] = nb1 + nnodz*(ez+1) + 1;   nodel_count_h[nb1 + nnodz*(ez+1) + 1]++;  
          # elnod_h[ei+6] = nb2 + nnodz*(ez+1) + 1;   nodel_count_h[nb2 + nnodz*(ez+1) + 1]++;  
          # elnod_h[ei+7] = nb2 + nnodz*(ez+1);       nodel_count_h[nb2 + nnodz*(ez+1)    ]++;  
    for ez in range (elem_z):          
      for ey in range (elem_y):    
        for ex in range (elem_x):   
          nb1 = ncz*ez + (elem_x + 1)*ey + ex
          nb2 = ncz*ez + (elem_x + 1)*(ey+1) + ex
          
          self.elnod.append((nb1           , nb1 + 1             ,nb2 + 1             ,nb2,
                             nb1+ncz*(ez+1), nb1 + ncz*(ez+1) + 1,nb2 + ncz*(ez+1) + 1,nb2 + ncz*(ez+1)))

    self.writeCenters()
    
#Based on: https://github.com/caosdoar/spheres/blob/master/src/spheres.cpp 
#https://medium.com/@oscarsc/four-ways-to-create-a-mesh-for-a-sphere-d7956b825db4
#OUTSIDE SURFACES IN RADIOSS IS CLOCKWISE LOOKING FROM OUTSIDE (IS LEFT HAND)
class Sphere_Mesh(Mesh):
  #NECESSARY TO CREATE SEPARATED NEW LISTS!
  nodes = []
  elnod = [] 

  def __init__(self, id, radius, ox,oy,oz, divisions):
    self.nodes = []
    self.elnod = []
    existin_vtx = np.zeros((6, divisions+1, divisions+1)).astype(int)
    rep = 0
    # print ("existing vtk ", existin_vtx)
    print ("Creating Sphere mesh")
    self.id = id
    CubeToSphere_origins = [
    Vector(-1.0, -1.0, -1.0), #ORGIINAL POINT ONE
    Vector(1.0, -1.0, -1.0),
    Vector(1.0, -1.0, 1.0),
    Vector(-1.0, -1.0, 1.0),
    Vector(-1.0, 1.0, -1.0),
    Vector(-1.0, -1.0, 1.0)]
    CubeToSphere_rights = [
    Vector(2.0, 0.0, 0.0),
    Vector(0.0, 0.0, 2.0),
    Vector(-2.0, 0.0, 0.0),
    Vector(0.0, 0.0, -2.0),
    Vector(2.0, 0.0, 0.0),
    Vector(2.0, 0.0, 0.0)]
    CubeToSphere_ups = [
		Vector(0.0, 2.0, 0.0),
		Vector(0.0, 2.0, 0.0),
		Vector(0.0, 2.0, 0.0),
		Vector(0.0, 2.0, 0.0),
		Vector(0.0, 0.0, 2.0),
		Vector(0.0, 0.0, -2.0) ]
    step = 1.0 / divisions
    step3 = Vector(step, step, step)
    
    
    n = 0
    for face in range (6): #CUBE FACES 
      origin = CubeToSphere_origins[face]
      right = CubeToSphere_rights[face]
      # print (right)
      up = CubeToSphere_ups[face]
      for j in range (divisions+1):
        j3 = Vector(j,j,j)
        for i in range (divisions+1):
          i3 = Vector(i,i,i)
          put_node = True
          # print ("i3 j3 ", i3, j3)
          # print (right)
          # print ("origin ")
          # print (origin)
          # print ("right * origin ")

          # const Vector3 p = origin + step3 * (i3 * right + j3 * up);
          p = origin + ( step3 * (i3 * right  + up *j3 )  )
          p2 = p * p
          
          rx = p.components[0] * sqrt(1.0 - 0.5 * (p2.components[1] + p2.components[2]) + p2.components[1]*p2.components[2]/3.0)
          ry = p.components[1] * sqrt(1.0 - 0.5 * (p2.components[2] + p2.components[0]) + p2.components[2]*p2.components[0]/3.0)
          rz = p.components[2] * sqrt(1.0 - 0.5 * (p2.components[0] + p2.components[1]) + p2.components[0]*p2.components[1]/3.0)
          
          x = rx * radius + ox;           y = ry * radius + oy ;           z = rz * radius + oz;
          # print ("z , z corrected ", rz,z)
          
          # print ("node ", n, ", coords " ,x,y,z)
          existin_vtx[face][i][j] = n 
          
          for k in range (n): #CHECK IF THERE IS AN EXISTENT NODE THERE
            if ( abs(x - self.nodes[k][0])<1.0e-4 and abs(y - self.nodes[k][1])<1.0e-4 and abs(z - self.nodes[k][2])<1.0e-4 ):
              # print ("FOUND SIMILAR X in node ", k ,"face", face, "i, j ", i, j, "pos: ", x,y,z)
              rep = rep + 1
              put_node = False
              existin_vtx[face][i][j] = k 
          

          if (put_node):
            self.nodes.append((x,y,z))
            # print ("vertex ", n)
            n = n +1
    
    # print ("existing vtk ", existin_vtx)
    print ("repeated nodes: ", rep)
    self.nodes.append((ox,oy,oz)) #CENTER AS RIGID PIVOT
    print ("Sphere Origin: ", ox,oy,oz)
    self.node_count = n + 1
    
    print ("Sphere generated: %d", n , " nodes      ")
    # print ("Node vector count: ", len(self.nodes))
    
      # print (origin)
    
    # for i in range (self.node_count):
      # print ("SPHERE Node ", i, self.nodes[i])

    # ORIGINAL 
    e = 0
    for face in range (6): #CUBE FACES
      for ey in range (divisions):
        for ex in range (divisions):  
          # self.elnod.append(((divisions+1)*ey+ex,(divisions+1)*ey + ex+1,(divisions+1)*(ey+1)+ex+1,(divisions+1)*(ey+1)+ex))      
          # print ("connectivity: ",(divisions+1)*ey+ex,(divisions+1)*ey + ex+1,(divisions+1)*(ey+1)+ex+1,(divisions+1)*(ey+1)+ex)  
          # print ("connectivity: ",existin_vtx[face][ex][ey], existin_vtx[face][ex+1][ey], existin_vtx[face][ex+1][ey+1], existin_vtx[face][ex][ey+1])
          self.elnod.append((existin_vtx[face][ex][ey], existin_vtx[face][ex+1][ey], existin_vtx[face][ex+1][ey+1], existin_vtx[face][ex][ey+1]))
          e = e + 1
    self.elem_count = e
    

class Spring_Mesh(Mesh):
  nodes = []
  elnod = []
  type = "spring"
  def __init__(self, id, n1 = 0, n2 = 0):
    #super(Spring_Mesh, self).__init__()
    self.id = id
    self.elnod = []
    self.nodes = []
    #self.elnod.append(n1,n2)
  def __init__(self, id ):
    #super(Spring_Mesh, self).__init__()
    self.id = id
    self.elnod = []
    self.nodes = []
    #self.elnod.append((0,0))
  def add_elem(self,n1,n2):
    self.elnod.append((n1,n2))
    self.elem_count+=1
    


def plane_mesh(length, delta, nodos, elnod, mesh):
  num_nodos = 10
  num_elem_xy = ()
  # nodos = np.empty(num_nodos,dtype=object)
  # y = np.arange(30).reshape((10, 3)) 
  nodos.append((1,1,1))
  # print("\nArray y : ", y) 
  # np.reshape(nodos,(20,num_nodos))
  # print (nodos)
  # print (nodos[0][2])
  
class NodeGroup:
  nodes = [] # TODO: CHANGE TO LIST
  part = 0
  def __init__ (self, id):
    self.id = id

class Prop: 
  thck = 5.0e-4
  type = "shell"
  def __init__(self, pid, t):
    self.pid = pid
    self.thck = t
    self.type = "shell"
  def printRadioss(self,f):     
    #if (type=="shell"):
    f.write("##--------------------------------------------------------------------------------------------------\n")
    f.write("## Shell Property Set (pid 1)\n")
    f.write("##--------------------------------------------------------------------------------------------------\n")
    f.write("/PROP/SHELL/" + str(self.pid) + "\n")
    f.write("SECTION_SHELL:1 TITLE:probe_section  \n")                                                               
    f.write("#Ishell	Ismstr	Ish3n	Idril	 	 	P_thickfail\n")
    f.write("         4         2                         \n")                                   
    f.write("#hm	hf	hr	dm	dn\n")
    f.write("\n")
    f.write("#---1----|----2----|----3----|----4----|----5----|----6----|----7----|----8----|----9----|---10----|\n")
    f.write("#N	       Istrain	 Thick	             Ashear	 	           Ithick	Iplas    \n")                                                                                                
    f.write(writeIntField(2, 10) + "          " + writeFloatField(self.thck,20,6) + "                                       1         1\n")


class SpringProp(Prop):
  k = 1.0
  c = 0.0
  type = "spring"
  #else if (type=="spring"):    
  def __init__(self, pid, k):     
    self.pid = pid
    self.k = k
  def printRadioss(self,f):
    f.write("##--------------------------------------------------------------------------------------------------\n")
    f.write("## Spring Property Set (pid 1)\n")
    f.write("##--------------------------------------------------------------------------------------------------\n")
    f.write("/PROP/TYPE13/" + str(self.pid) + "\n")
    f.write("SECTION_SPRING TITLE:probe_section  \n")                                                               
    f.write("#--Mass	           |            Inertia|	Skew_ID |	sens_ID	|  Isflag	|  Ifail	|Ileng	Ifail2\n")
    f.write("         2.0e-6                                        \n")
    for k in range(6): #DOF                                   
      f.write("#---1----|----2----|----3----|----4----|----5----|----6----|----7----|----8----|----9----|---10----|\n")
      f.write("#                 K1	                 C1	                 A1	                 B1	                 D1\n")
      if (k<3):
        f.write(writeFloatField(self.k,20,6))
      else:
        f.write(writeFloatField(1.0e10,20,6))
      f.write(writeFloatField(1.0e2,20,6))
      for i in range(3):
        f.write(writeFloatField(0.0,20,6))
      f.write("\n")
      for i in range(5):
        f.write(writeIntField(0, 10))
      f.write("\n")
      for i in range(4):
        f.write(writeIntField(0, 20))
      f.write("\n")
    f.write("#                 V0              Omega0               F_cut   Fsmooth\n")
    f.write("                   0                   0                   0         0\n")
    f.write("#                  C                   n               alpha                beta\n")
    f.write("                   0                   0                   0                   0\n")
    f.write("                   0                   0                   0                   0\n")
    f.write("                   0                   0                   0                   0\n")
    f.write("                   0                   0                   0                   0\n")
    f.write("                   0                   0                   0                   0\n")
    f.write("                   0                   0                   0                   0\n")
    f.write("#---1----|----2----|----3----|----4----|----5----|----6----|----7----|----8----|----9----|---10----|\n")
         
     
class Material:
  thermal = False
  rho = 0.0
  ms_fac = 1.0
  vs_fac = 1.0
  def __init__(self, mid, th):
    self.thermal = th
    id = mid
  def printRadioss(self,f):
    f.write("/MAT/PLAS_JOHNS/2\n")  
    f.write("MAT_PIECEWISE_LINEAR_PLASTICITY:2 TITLE:mat_probe   \n")
    f.write(writeFloatField(self.rho,20,6) + "\n")
    #f.write("                7850.0\n")  
    f.write("#                  E                  Nu     Iflag  \n")
#    f.write("      200000000000.0                0.33\n")  
    f.write(writeFloatField(self.E,20,6) + writeFloatField(self.nu,20,6) +"\n")    
    f.write("#                  a                   b                   n             EPS_max            SIG_max0\n")
#    f.write("         359000000.0         327000000.0               0.4541.00000000000000E+301.00000000000000E+30\n")
    f.write(writeFloatField(self.Ajc,20,6) + writeFloatField(self.Bjc,20,6) + writeFloatField(self.njc,20,6) + "1.00000000000000E+301.00000000000000E+30\n")    
    f.write("#                  c           EPS_DOT_0       ICC   Fsmooth               F_cut               Chard\n")    
    #f.write("              0.0786                0.04         1         11.00000000000000E+30\n")
    f.write(writeFloatField(self.Cjc,20,6) + writeFloatField(self.e0jc,20,6) + "         1         11.00000000000000E+30\n")
    f.write("#                  m              T_melt              rhoC_p                 T_r\n")    
    f.write("               0.919               1500."+writeFloatField(self.rho*self.cp_th*self.ms_fac,20,6) +"                   0\n")
    # if (self.thermal):    
    f.write("#/HEAT/MAT/mat_ID/unit_ID\n")
    f.write("/HEAT/MAT/2\n")
    f.write("#                 T0             RHO0_CP                  AS                  BS     IFORM\n")
    #f.write("              20.0                 2.5e6               15.0                  0.0        1\n")
    f.write("                20.0" + writeFloatField(self.rho*self.cp_th*self.ms_fac,20,6) + writeFloatField(self.vs_fac*self.k_th,20,6) + "                 0.0        1\n")
    f.write(" \n") #REQUIRED

    
class Function:
  val_count = 0 
  def __init__(self, id, x,y):
    self.val_count = 1
    self.vals = []
    self.vals.append((x,y))
    self.id = id
    #print ("function id ", id)
  def Append (self,x,y):
    self.vals.append((x,y))
    self.val_count = self.val_count + 1
  def getVal(self, i):
    return self.vals[i]
  def getVal_ij(self, i, j):
    return self.vals[i][j]
  def print(self,f):
    line = "/FUNCT/%d\n" % (self.id)
    line = line + "F_FUNC_%d\n" % (self.id)
    for val in range (self.val_count):
      line = line + writeFloatField(self.getVal(val)[0],20,6) + \
                    writeFloatField(self.getVal(val)[1],20,6) + "\n"
    f.write(line)  

#ASSUMING EACH PART HAS ONLY 1 MESH
class Part:
  is_rigid = False
  is_moving = False
  is_support = False
  id_grn_move = 0 #GROUP NODE FOR MOVING
  pid         = 1
  stiffk_     = 1.0e5    
  elcon_renumber = True #TEMPORARY, ONLY UNTIL VECTOR OF NODES WILL BE A VECTOR OF CLASSES     
  
  def __init__(self, mid):
    self.id = mid
    self.mesh = []
    self.title = "PART_ID_%d\n" %mid
    self.mid = 0
    self.id_grn_move = mid + 100
    print("Creating part " + str(self.id,) + " function\n")
    self.temp_fnc = Function(self.id,0.0,0.0)
    self.elcon_renumber = True
    
  def asignPropID (self, pi):
    self.pid = pi
    
  def AppendMesh(self,m):
    if (not isinstance(m, Mesh)):
      print ("part is not a mesh")
    else:
      self.mesh.append(m)
  
  def printRadioss(self,f): 
    if (self.mesh[0].type == "shell"):
      f.write('/SHELL/' + str(self.id) + '\n')
    if (self.mesh[0].type == "solid"):
      f.write('/BRICK/' + str(self.id) + '\n')
    if (self.mesh[0].type == "spring"):
      f.write('/SPRING/' + str(self.id) + '\n')
    print("Printing Elements..\n")
    #print ("initial node ",self.mesh[0].ini_node_id+ self.mesh[0].ini_node_id)
    #print ("node: ", self.mesh[0].elnod[0][0])
    if (self.elcon_renumber):
      start_id = self.mesh[0].ini_node_id
    else:
      start_id = 0
    for i in range (self.mesh[0].elem_count):#self.mesh[0].elem_count):
      line = writeIntField(i + self.mesh[0].ini_elem_id ,10)
      for d in range (np.size(self.mesh[0].elnod,1)):
        # print (self.mesh[0].ini_node_id, ", ")
        line = line + writeIntField(self.mesh[0].elnod[i][d] + start_id,10)
      if (i%100==0):
        print ("Element ",i)
      f.write(line + '\n')   
    
    line = "/PART/%d\n" % self.id
    f.write(line)
    f.write(self.title)                                                                                            
    f.write("#     pid     mid\n")
    f.write(writeIntField(self.pid, 10) + "         2\n") 
    line = "/GRNOD/PART/%d\n" % self.id    
    line = line + "PART_%d\n" % self.id
    line = line + writeIntField(self.id,10) + "\n"
    f.write(line)
    
    #GRNOD FOR MOVE (IF CONTACT SUPPORT)
    if (self.is_rigid or self.is_moving):
      line = "/GRNOD/NODE/%d\n" % self.id_grn_move    
      line = line + "MOVE_%d\n" % self.id
      line = line + writeIntField(self.mesh[0].ini_node_id + self.mesh[0].node_count - 1, 10) + "\n"
      f.write(line)
    if (self.is_moving or self.is_support):
      line = "/BCS/%d\n" % self.id
      line = line + "BoundSpcSet_1 \n"  
      line = line + "#  Tra rot   skew_ID  grnod_ID\n"
      if (self.is_moving): #LEDDING A TOOL OR A SPRING
        line = line + "   000 111         0" + writeIntField(100+self.id, 10) + "\n"
      if (self.is_support):         
        line = line + "   110 111         0" + writeIntField(100+self.id, 10) + "\n"
      f.write(line)

    
    if (self.mesh[0].print_segments):
      self.mesh[0].printESurfsRadioss(f) 

    if (self.is_rigid):
      self.mesh[0].printRigidRadioss(f) 
      self.mesh[0].printContSurfRadioss(f)
    else:
      self.mesh[0].printPartSurfRadioss(f) #ONLYFOR CONVECTION

class Interface:
  id_master = 0
  id_slave = 0
  bc_count = 0
  def __init__(self, master, slave):
    self.id_master = master
    self.id_slave = slave
  
class Model:
  tot_nod_count = 0
  tot_ele_count = 0
  thermal = False
  node_group_count = 0
  cont_support = True
  starter_file = ""
  double_sided = True
  min_dt = 1.0e-4
  #end_proc_time = 0.0 #Before release
  vscal_fac = 1.0
  mass_scal = False
  ms_dtsize = 1.0e-4
  dampfac   = 0.0
  
  
  def __init__(self):
    self.part_count = 0
    self.part = []
    self.mat = []
    self.prop = []
    self.load_fnc = []
    self.inter = []
    self.node_group = []
    self.starter_file = ""
    self.supp_fnc = []
    self.multi_tool=False
    self.multi_tool_N=2
    self.end_proc_time=0.0

  def set_end_time(self, inc_file=None, end_time=None):
    try:
      if inc_file is None and end_time is None:
        raise ValueError("file or end time must be specified")
    
      if inc_file is None:
        self.end_proc_time = end_time
        return
        
      if end_time is None:
        with open(inc_file, 'r') as file:
          lines = file.readlines()
        self.end_proc_time = float(lines[-1].split()[0])  # Convertir el primer valor a float
        print("Last line:", lines[-1])
        print("End processing time:", self.end_proc_time)
    
    except FileNotFoundError:
      print("Error: The specified file does not exist.")
    except ValueError as ve:
      print(ve)  # Para manejar el error de valores no especificados
    except Exception as e:
      print(f"An unexpected error occurred: {e}")
      
    
  def set_Multi_tool(self,multi_tool_N):
    print("set multitool to:", multi_tool_N)
    if multi_tool_N>2: 
        self.multi_tool=True
    self.multi_tool_N=multi_tool_N
      
  def AppendPart(self, p):
    if (not isinstance(p, Part)):
      print ("ERROR: added object is not a part ")
    else:
      self.part.append(p)
      self.part_count = self.part_count + 1
      print ("part count ", self.part_count)
      if (self.part_count > 1):
        
        self.part[self.part_count-1].mesh[0].ini_node_id = self.tot_nod_count + 1
        
        self.tot_ele_count = self.tot_ele_count + self.part[self.part_count-2].mesh[0].elem_count
        self.part[self.part_count-1].mesh[0].ini_elem_id = self.tot_ele_count + 1
      
      self.tot_nod_count = self.tot_nod_count + self.part[self.part_count-1].mesh[0].node_count  

    print ("Added part, id: ", self.part[self.part_count-1].id)
    print ("Part ", self.part_count, " initial node: ", self.part[self.part_count-1].mesh[0].ini_node_id, "end node: ", self.tot_nod_count)
    
  def AppendInterface(self, i):
    if (not isinstance(i, Interface)):
      print ("ERROR: added object is not a interface ")
    else:
      self.inter.append(i)
      
  def AppendMat(self, m):
    if (not isinstance(m, Material)):
      print ("ERROR: added object is not a part ")
    else:
      self.mat.append(m)

  def AppendLoadFunction(self, lf):
    self.load_fnc.append(lf)
    
  def AppendProp(self, p):
    print ("APPENDING PROP")
    if (not isinstance(p, Prop)):
      print ("ERROR: added object is not a part ")
    else:
      self.prop.append(p)
      
      
  def printInterfaces(self,f):
    f.write("#-  9. INTERFACES:\n")  
    for i in range (len(self.inter)):
      fric = 0.0
      f.write("#---1----|----2----|----3----|----4----|----5----|----6----|----7----|----8----|----9----|---10----|\n")
      f.write("/INTER/TYPE7/%d\n" % (i))
      f.write("INTERFACE %d\n" % (i))
      f.write("#  Slav_id   Mast_id      Istf      Ithe      Igap                Ibag      Idel     Icurv      Iadm\n")
      line = writeIntField(self.inter[i].id_slave,10) + writeIntField(self.inter[i].id_master+1000000,10) 
      f.write(line)
      # WITHOUT ENDLINE
      if (not self.thermal):
        f.write("         0         0         0                   0         0         0         0\n")
      else:
          
        if self.double_sided:
          start_part=2
        else:
          start_part=1
            
        if (self.inter[i].id_master<self.multi_tool_N+start_part): #was 4
          f.write("         0         1         0                   0         0         0         0\n")          
        else: #Ithe=1
          f.write("         0         0         0                   0         0         0         0\n")
          
      f.write("#          Fscalegap             GAP_MAX             Fpenmax\n")
      f.write("                   0                   0                   0\n")
      f.write("#              Stmin               Stmax          %mesh_size               dtmin  Irem_gap\n")
      f.write("                   0                   0                   0                   0         0\n")
      f.write("#              Stfac                Fric              Gapmin              Tstart               Tstop\n")
      if (self.inter[i].id_master<self.multi_tool_N+start_part): #was 4 #FRICTION
        f.write("#                  1                  0.                  .0                   0                   0\n")
      else :
        f.write("#                  1                 1.0                  .0                   0                   0\n")
      f.write("                   1                 .0           0.0000                       0                   0\n")
      f.write("#      IBC                        Inacti                VisS                VisF              Bumult\n")
      f.write("       000                             0                   1                   1                   0\n")
      f.write("#    Ifric    Ifiltr               Xfreq     Iform   sens_ID\n")
      f.write("         0         0                   0         0         0\n")
      
      #TEHRMAL CONTACT FIELD
      if (self.thermal):
        if (self.inter[i].id_master<self.multi_tool_N+start_part): #was 4
          f.write("#---1----|----2----|----3----|----4----|----5----|----6----|----7----|----8----|----9----|---10----|\n")
          f.write("#-- Kthe	          |fct_IDK  |	 	      |         Tint	    |Ithe_form| -----AscaleK ---  |\n")
          f.write("15000               0                   0                   1\n")
          f.write("#---1----|----2----|----3----|----4----|----5----|----6----|----7----|----8----|----9----|---10----|\n")
          f.write("#----   Frad	      |       Drad	      |       Fheats	    |    Fheatm     -----\n")
          f.write("0                   0                   0                   0\n")

  
  # def printMovingPart(self,id,fid,f):
  def printMovingParts(self,f):
    func = 1000001
    for p in range(self.part_count):
      if (self.part[p].is_moving):
        f.write("/IMPDISP/%d\n"%(3*p+1))
        f.write("NUM3HS1D00_fixvel_1\n")
        f.write("#funct_IDT       Dir   skew_ID sensor_ID  grnod_ID  frame_ID     Icoor\n") 
        f.write(writeIntField(func,10) + "         X         0         0" + writeIntField(self.part[p].id+100,10) + "         0         0\n")
        f.write("#           Ascale_x            Fscale_Y              Tstart               Tstop\n")
        f.write("                   1                   1                   0               11000  \n")                  
        f.write("/IMPDISP/%d\n"%(3*p+2))
        f.write("NUM3HS1D00_fixvel_1\n")
        f.write("#funct_IDT       Dir   skew_ID sensor_ID  grnod_ID  frame_ID     Icoor\n")
        f.write(writeIntField(func+1,10) + "         Y         0         0" + writeIntField(self.part[p].id+100,10) + "         0         0\n")
        f.write("#           Ascale_x            Fscale_Y              Tstart               Tstop\n")
        f.write("                   1                   1                   0               11000 \n")
        f.write("/IMPDISP/%d\n"%(3*p+3))
        f.write("NUM3HS1D00_fixvel_1\n")
        f.write("#funct_IDT       Dir   skew_ID sensor_ID  grnod_ID  frame_ID     Icoor\n")
        f.write(writeIntField(func+2,10) + "         Z         0         0" + writeIntField(self.part[p].id+100,10) + "         0         0\n")
        f.write("#           Ascale_x            Fscale_Y              Tstart               Tstop\n")
        f.write("                   1                   1                   0               11000 \n")
        func = func + 3
  def AddNodeSetOutsideBoxXY (self, id, v1, v2):
    self.node_group.append(NodeGroup(id))
    nc = 0
    for p in range (self.part_count):
      # print ("ini node id ",self.part[p].mesh[0].ini_node_id )
      for n in range (self.part[p].mesh[0].node_count):
        inc = False
        for d in range (2):
          if (self.part[p].mesh[0].nodes[n][d] < v1.components[d] or self.part[p].mesh[0].nodes[n][d] > v2.components[d]):
            inc = True
            # print ("comp, bound", self.part[p].mesh[0].nodes[n][d], v1.components[d],v2.components[d])
        if (inc): 
          self.node_group[self.node_group_count].nodes.append(self.part[p].mesh[0].ini_node_id + n)   
          nc = nc +1
    self.node_group_count =   self.node_group_count + 1
    print ("Outside Box Set Node count: ", nc)
        

  def printFixNodeGroups(self,f):
    for g in range (self.node_group_count):
      # print ("Writing set of count: ", len (self.node_group[g].nodes))
      f.write("/GRNOD/NODE/%d\n" % self.node_group[g].id)
      f.write("FIX_%d\n" % self.node_group[g].id)
      ff = 0;
      line = ""
      for i in range (len (self.node_group[g].nodes)):
        # print ("i ",i, "id ", self.node_group[g].nodes[i], "line ", line  )
        line = line + writeIntField(self.node_group[g].nodes[i],10)
        ff = ff + 1
        if (ff ==10):
          ff = 0
          f.write(line + "\n")
          line = ""
      if (ff>0):
        f.write(line + "\n")    
      f.write("/BCS/%d\n" % self.node_group[g].id)
      f.write("BoundSpcSet_1\n")     
      f.write("#  Tra rot   skew_ID  grnod_ID\n")      
      f.write("   111 111         0" + writeIntField(self.node_group[g].id,10) + "\n")         

  
  def printRadioss(self,fname):
    self.starter_file = fname
    print ("WRITING RADIOSS INPUT\n")
    f = open(fname + "_0000.rad","w+")
    f.write("#RADIOSS STARTER\n")
    f.write("/BEGIN\n")
    f.write("test                                                        \n")                   
    f.write("      2019         0 \n")
    f.write("                  kg                   m                   s\n")
    f.write("                  kg                   m                   s\n")
    if(not(self.multi_tool)):
      f.write("#include movi_x0.inc\n")
      f.write("#include movi_y0.inc\n")
      f.write("#include movi_z0.inc\n")
      if (self.double_sided):
        f.write("#include movi_x1.inc\n")
        f.write("#include movi_y1.inc\n")
        f.write("#include movi_z1.inc\n")
    else:
      for i in range(self.multi_tool_N):
        f.write(f'#include movi_x{i}.inc\n')
        f.write(f'#include movi_y{i}.inc\n')
        f.write(f'#include movi_z{i}.inc\n')
        
    f.write('/NODE\n')
    for p in range (self.part_count):
      print ("part node count ", self.part[p].mesh[0].node_count)
      for i in range (self.part[p].mesh[0].node_count):
        # print ("Node ", self.part[p].mesh[0].nodes[i])
        line = writeIntField(i + self.part[p].mesh[0].ini_node_id,10)
        for d in range (3):
          line = line + writeFloatField(self.part[p].mesh[0].nodes[i][d],20,6) 
        f.write(line + '\n')

    # Print element connectivity

    for p in range (self.part_count):
      print("Printing part"+str(p))
      self.part[p].printRadioss(f)
      print("Printing convection...\n")
      if (self.part[p].id == 1):
        self.part[p].mesh[0].printConvRadioss(self.vscal_fac,f)
        
    
    print ("printing materials: ", len(self.mat))
    for m in range (len(self.mat)):
      self.mat[m].printRadioss(f)

    for p in range(len(self.prop)):
      self.prop[p].printRadioss(f)
      
    if (self.thermal):
      print("Printing heat things\n")
      for lf in range(self.multi_tool_N):
        print("Temperature Part"+str(lf+1))
        self.part[lf+1].temp_fnc.print(f)
        #print("part count \n", lf+2)
        #line = "/FUNCT/%d\n" % (lf+2)
        #line = line + "F_TOOL_%d\n" % (lf+2)
        #for val in range (self.part[p].temp_fnc.val_count):
        #  line = line + writeFloatField(self.part[p].temp_fnc.getVal(val)[0],20,6) + \
        #                writeFloatField(self.part[p].temp_fnc.getVal(val)[1],20,6) + "\n"
        #f.write(line)

      #print ("Load function count: ", len(self.load_fnc))
      ### LOAD FNC
      #for lf in range (len(self.load_fnc)):
      #  line = "/FUNCT/%d\n" % (lf+1)
      #  line = line + "F_ELEM_%d\n" % (lf+1)
      #  for val in range (self.load_fnc[lf].val_count):
      #    line = line + writeFloatField(self.load_fnc[lf].getVal(val)[0],20,6) + \
      #                   writeFloatField(self.load_fnc[lf].getVal(val)[1],20,6) + "\n"
      #  f.write(line)

      #f.write("################################### ELEMENT FLUXES #####################################\n")
      #for lf in range (len(self.load_fnc)):
      #  line = "/IMPFLUX/%d\nFLUX_ELEM%d\n" % (lf+1,lf+1)
      #  line = line + writeIntField(lf+1,10)+ writeIntField(lf+1,10) + "\n"
      #  line = line + "       1.0       1.0\n"
      #  f.write(line)
      #APPLY TEMP TO THE TOOL
#TEST
        # if (lf== 0 or (lf==1 and self.double_sided) ): 
        #   print(f"imptTemp to part {lf+1}")
        #   line = "/IMPTEMP/%d\nTOOL_TEMP%d\n" % (lf+2,lf+2)
        #   line = line + "#---1----|----2----|----3----|----4----|----5----|----6----|----7----|----8----|\n"
        #   line = line + "#fct_IDT	 sens_ID	 grnd_ID\n"	
        #   line = line + writeIntField(lf+2,10)+ "         0" + writeIntField(lf+2,10) + "\n"      
        #   line = line + "#---1----|----2----|----3----|----4----|----5----|----6----|----7----|----8----|\n"
        #   line = line + "       1.0       1.0\n"
        
        if (lf<=self.multi_tool_N):
          print(f"imptTemp to part {lf+1}")
          line = "/IMPTEMP/%d\nTOOL_TEMP%d\n" % (lf+2,lf+2)
          line = line + "#---1----|----2----|----3----|----4----|----5----|----6----|----7----|----8----|\n"
          line = line + "#fct_IDT	 sens_ID	 grnd_ID\n"	
          line = line + writeIntField(lf+2,10)+ "         0" + writeIntField(lf+2,10) + "\n"      
          line = line + "#---1----|----2----|----3----|----4----|----5----|----6----|----7----|----8----|\n"
          line = line + "       1.0       1.0\n"
          
            
          f.write(line)
            
    self.printInterfaces(f)
    
    #IF NO RELEASE
    self.printFixNodeGroups(f)
    
    self.printMovingParts(f)
    
    #IF MASS SCALING
    # f.write("/GRPART/PART/1\nPART_GROUP_FOR_AMS\n1\n")
    # f.write("/AMS\n1\n")
    # f.write("\n")
    
    
    # f.write("/TH/RBODY/1\n")
    # f.write("TH_NAME1 \n")
    # f.write("FX        FY        FZ        \n")
    # f.write("200\n")  
    
    f.write("/TH/PART/1\n")
    f.write("TH_NAME1 \n")
    f.write("DEF\n")

        
    
    if (self.cont_support):
      ## SUPPORT RELEASE THING
      for velf in range(len(self.supp_fnc)):
        self.supp_fnc[velf].print(f)
      
      print ("Printing Node groups %d \n" % (self.node_group_count))
      for lf in range (1, 9):
        # print ("fn ", self.load_fnc[lf][0], "\n")
        line = "/IMPVEL/%d\nVEL_SUPP%d\n" % (lf+1,lf+1)
        line = line + "#funct_IDT       Dir   skew_ID sensor_ID  grnod_ID  frame_ID     Icoor\n"
        line = line + writeIntField(self.supp_fnc[0].id,10) + "         Z         0         0" + writeIntField (100+1+self.multi_tool_N+lf,10) + "         0         0\n"
        line = line + "#           Ascale_x            Fscale_Y              Tstart               Tstop\n"
        if lf % 2 == 0:
          fscale = writeIntField(1,20)
        else:
          fscale = writeIntField(-1,20)
        line = line + "                   0" + fscale + "                   0               11000\n"
        line = line + "#---1----|----2----|----3----|----4----|----5----|----6----|----7----|----8----|----9----|---10----|\n"
        f.write(line)

    if (self.dampfac > 0.0):
      print("Added Dampint factor of "+str(self.dampfac))
      line = "/DAMP/1\n"+"MASS_DAMP_1\n"+writeFloatField(self.dampfac,20,6)+writeFloatField(0.0,20,6)+"         1\n"
      f.write(line)
    else:
      print("No Damping was added.")
      
    f.write('/END\n')
    
  def printEngine(self, run, time, dt, dthis):
    f = open(self.starter_file + "_000" + str(run) + ".rad","w+")
    f.write("/ANIM/DT\n")
    f.write("0 " +str(dt) + "\n")
    f.write("/ANIM/VECT/DISP\n")
    f.write("/ANIM/VECT/VEL\n")
    f.write("/ANIM/VECT/ACC\n")
    f.write("/ANIM/VECT/CONT\n")
    f.write("/ANIM/SHELL/TENS/STRESS/UPPER\n")
    f.write("/ANIM/SHELL/TENS/STRESS/LOWER\n")
    f.write("/ANIM/BRICK/TENS/STRESS\n")
    f.write("/ANIM/ELEM/EPSP\n")
    f.write("/ANIM/ELEM/ENER\n")
    f.write("/ANIM/SHELL/EPSP/UPPER\n")
    f.write("/ANIM/SHELL/EPSP/LOWER\n")
    f.write("/ANIM/SHELL/THIC\n")
    f.write("/ANIM/NODA/TEMP\n")
    f.write("/ANIM/NODA/P\n")
    f.write("/ANIM/VECT/FINT\n")
    f.write("/ANIM/VECT/FEXT\n")
    f.write("/ANIM/VECT/FOPT\n")
    f.write("/ANIM/VECT/FREAC\n")
    #IF MASS SCAL
    # f.write("/DT/AMS\n0.67 " +str(self.min_dt) + "\n")
    
    f.write("/RUN/" + self.starter_file + "_0000.rad" + "/1/\n")
    f.write(str(self.end_proc_time)+ "\n")
    f.write("/TFILE/3\n")
    	# No value: Built-in format of current Radioss version.
# = 1
# Binary (not readable by most Radioss post-processors)
# = 2
# Coded ASCII 32-bit
# = 3
# ASCII
# = 4 (Default)
# Binary IEEE 32-bit
    f.write(str(dthis) + "\n")
    f.write("/STOP\n")
    f.write("0 1e+08 0 1 1\n")
    if (self.mass_scal):
      f.write("/DT/NODA/CST/0\n")
      f.write("0.67   "+str(self.ms_dtsize)+"\n")

  def printRelease(self, run, time, dt, dthis):
    f = open(self.starter_file + "_000" + str(run) + ".rad","w+")
    f.write("/RUN/" + self.starter_file + "/" + str(run) + "\n")
    f.write(str(time)+"\n")
    f.write("/ANIM/DT\n")
    f.write("0 " +str(dt) + "\n")
    f.write("/ANIM/VECT/DISP\n")
    f.write("/ANIM/VECT/VEL\n")
    f.write("/ANIM/VECT/ACC\n")
    f.write("/ANIM/VECT/CONT\n")
    f.write("/ANIM/SHELL/TENS/STRESS/UPPER\n")
    f.write("/ANIM/SHELL/TENS/STRESS/LOWER\n")
    f.write("/ANIM/BRICK/TENS/STRESS\n")
    f.write("/ANIM/ELEM/EPSP\n")
    f.write("/ANIM/ELEM/ENER\n")
    f.write("/ANIM/SHELL/EPSP/UPPER\n")
    f.write("/ANIM/SHELL/EPSP/LOWER\n")
    f.write("/ANIM/SHELL/THIC\n")
    f.write("/ANIM/NODA/TEMP\n")
    f.write("/ANIM/NODA/P\n")
    f.write("/ANIM/VECT/FINT\n")
    f.write("/ANIM/VECT/FEXT\n")
    f.write("/ANIM/VECT/FOPT\n")
    f.write("/ANIM/VECT/FREAC\n")
    f.write("/RBODY/ON\n")
    for p in range(self.part_count):
      if (self.part[p].is_rigid):
        f.write(str(self.part[p].mesh[0].getRigidNode()) + " ")
    f.write("\n")
    
    f.write("/TFILE\n")
    f.write(str(dthis) + "\n")
    f.write("/PRINT/-1\n")
    f.write("/RFILE\n")
    f.write(" 20000 0 0\n")
    f.write("/MON/ON   \n")
    if (self.mass_scal):
      f.write("/DT/NODA/CST/0\n")
      f.write("0.67   "+str(self.ms_dtsize)+"\n")
    f.write("\n")
    # f.write("#INTERFACES REMOVING:\n")
    # f.write("/DEL/INTER\n")
    # for i in range (len(self.inter)):
      # f.write(str(i) + " ")
    f.write("\n\n")
    
    # f.write("#ADDED BOUNDARY CONDITIONS:\n")
    # f.write("/BCS/TRA/XYZ/\n")
    # for p in range(self.part_count):
      # if (self.part[p].is_rigid):
        # f.write(str(self.part[p].mesh[0].getRigidNode()) + " ")
    # f.write("\n")

    # f.write("/BCS/ROT/XYZ/\n")
    # for p in range(self.part_count):
      # if (self.part[p].is_rigid):
        # f.write(str(self.part[p].mesh[0].getRigidNode()) + " ")
    # f.write("\n")
    
    # f.write("/BCS/TRA/Z/\n")
    # f.write("1\n")
    
    # f.write("####################\n")
    # f.write("# IMPLICIT OPTIONS #\n")
    # f.write("####################\n")

    # f.write("/IMPL/PRINT/NONL/-1\n")
    # f.write("/IMPL/SOLVER/1\n")
    # f.write("# IPREC L_LIM ITOL L_TOL\n")
    # f.write(" 0 0 0 0.\n")
    # f.write("/IMPL/NONLIN/1\n")
    # f.write("# upd_K_LIM NITOL N_TOL\n")
    # f.write(" 2 0 0.25e-1\n")
    # f.write("/IMPL/DTINI\n")
    # f.write(" 0.08\n")
    # f.write("/IMPL/DT/STOP\n")
    # f.write("# DT_MIN DT_MAX\n")
    # f.write(" 0.1e-4 0.0\n")
    # f.write("/IMPL/DT/2\n")
    # f.write("# NL_DTP SCAL_DTP NL_DTN SCAL_DTN\n")
    # f.write(" 6 .0 20 0.67 0.0\n")
    # f.write("/IMPL/SPRBACK\n")
    
  def printDynRelax(self, run, time, dt, dthis):
    f = open(self.starter_file + "_000" + str(run) + ".rad","w+")
    f.write("/RUN/" + self.starter_file + "/" + str(run) + "\n")
    f.write(str(time)+"\n")
    f.write("/ANIM/DT\n")
    f.write("0 " +str(dt) + "\n")
    f.write("/ANIM/VECT/DISP\n")
    f.write("/ANIM/VECT/VEL\n")
    f.write("/ANIM/VECT/ACC\n")
    f.write("/ANIM/VECT/CONT\n")
    f.write("/ANIM/SHELL/TENS/STRESS/UPPER\n")
    f.write("/ANIM/SHELL/TENS/STRESS/LOWER\n")
    f.write("/ANIM/BRICK/TENS/STRESS\n")
    f.write("/ANIM/ELEM/EPSP\n")
    f.write("/ANIM/ELEM/ENER\n")
    f.write("/ANIM/ELEM/HOUR   \n")                                 
    f.write("/ANIM/SHELL/EPSP/UPPER\n")
    f.write("/ANIM/SHELL/EPSP/LOWER\n")
    f.write("/ANIM/SHELL/THIC\n")
    f.write("/ANIM/NODA/TEMP\n")
    f.write("/ANIM/NODA/P\n")
    f.write("/ANIM/VECT/FINT\n")
    f.write("/ANIM/VECT/FEXT\n")
    f.write("/ANIM/VECT/FOPT\n")
    f.write("/ANIM/VECT/FREAC\n")
    # /RBODY/ON
    # 3392 3648 3904 4160 4416 4672 4928 5184 5337 
    f.write("/TFILE\n")
    f.write(str(dthis) + "\n")
    f.write("/PRINT/-1\n")
    f.write("/RFILE\n")
    f.write(" 20000 0 0\n")
    f.write("/MON/ON   \n")
    if (self.mass_scal):
      f.write("/DT/NODA/CST/0\n")
      f.write("0.67   "+str(self.ms_dtsize)+"\n")
    f.write("\n")
    f.write("/ADYREL\n")
    f.write(" \n")
    f.write("/ANIM/ELEM/HOUR             \n")                       
    f.write("/ANIM/SHELL/TENS\n")


class ThermalSolidModel(Model):
  def __init__(self):
    self.part_count = 0
    self.part = []
    self.mat = []
    self.prop = []
    self.load_fnc = []
    self.inter = []
    self.node_group = []
    self.starter_file = ""
    self.supp_fnc = []
    
  def printRadioss(self,fname):
    self.starter_file = fname
    print ("WRITING RADIOSS INPUT\n")
    f = open(fname + "_0000.rad","w+")
    f.write("#RADIOSS STARTER\n")
    f.write("/BEGIN\n")
    f.write("test                                                        \n")                   
    f.write("      2019         0 \n")
    f.write("                  kg                   m                   s\n")
    f.write("                  kg                   m                   s\n")
    f.write("#include movi_x.inc\n")
    f.write("#include movi_y.inc\n")
    f.write("#include movi_z.inc\n")
    if (self.double_sided):
      f.write("#include movo_x.inc\n")
      f.write("#include movo_y.inc\n")
      f.write("#include movo_z.inc\n")
    f.write('/NODE\n')
    for p in range (self.part_count):
      print ("part node count ", self.part[p].mesh[0].node_count)
      for i in range (self.part[p].mesh[0].node_count):
        # print ("Node ", self.part[p].mesh[0].nodes[i])
        line = writeIntField(i + self.part[p].mesh[0].ini_node_id,10)
        for d in range (3):
          line = line + writeFloatField(self.part[p].mesh[0].nodes[i][d],20,6) 
        f.write(line + '\n')

    # Print element connectivity
    for p in range (self.part_count):
      self.part[p].printRadioss(f)
      if (not self.part[p].is_rigid):
        self.part[p].mesh[0].printConvRadioss(self.vscal_fac,f)
        
    
    print ("printing materials: ", len(self.mat))
    for m in range (len(self.mat)):
      self.mat[m].printRadioss(f)
    
    
    if (self.thermal):
      # f.write("#include thermal.inc\n")  
      print ("Load function count: ", len(self.load_fnc))
      ### LOAD FNC
      for lf in range (len(self.load_fnc)):
        # print ("fn ", self.load_fnc[lf][0], "\n")
        line = "/FUNCT/%d\n" % (lf+1)
        line = line + "F_ELEM_%d\n" % (lf+1)
        for val in range (self.load_fnc[lf].val_count):
          line = line + writeFloatField(self.load_fnc[lf].getVal(val)[0],20,6) + \
                        writeFloatField(self.load_fnc[lf].getVal(val)[1],20,6) + "\n"
        f.write(line)

      f.write("################################### ELEMENT FLUXES #####################################\n")
      for lf in range (len(self.load_fnc)):
        # print ("fn ", self.load_fnc[lf][0], "\n")
        line = "/IMPFLUX/%d\nFLUX_ELEM%d\n" % (lf+1,lf+1)
        line = line + writeIntField(lf+1,10)+ writeIntField(lf+1,10) + "\n"
        line = line + "       1.0       1.0\n"
        f.write(line)
      
    for p in range(len(self.prop)):
      self.mat[p].printRadioss(f)
