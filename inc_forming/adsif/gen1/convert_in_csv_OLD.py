import csv
import numpy as np

###### PARAM ENTRADA ##############
##### ASSUMES THAT UNITS ARE MM####
## AND CSV IS IN MM
vel = 600.0; #mm/min
#THEY ARE USED TO CORRECT INITIAL Z
gap_0       = 0.0e-4
dt_dum      = 1.0e-3 #Positioning
thck        = 5.0e-4

av_dist = 0.9
dt = av_dist  / vel

#NEW, THIS ACCOMODATES TOOL TO ABS Z POSITION
t_interf = 1.0
#### IN TOP TOOL t/2 + disp = zabs
#ZABS IS GIVEN BY TOOLTIP POINTS

###################################
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
  
#Put on list...
out_x = open('movi_x.inc',"w")
out_y = open('movi_y.inc',"w")
out_z = open('movi_z.inc',"w")


file = open('myToolpath_topToolTipPnts.csv')

reader = csv.reader(file)

data = list(csv.reader(file, delimiter=','))
# data = list(reader)

print (data[1][1])

pt_count  = len(data) - 1

print ("Point Count: ", pt_count)


out_x.write("/FUNCT/1000001\nmovx\n")    
out_y.write("/FUNCT/1000002\nmovy\n")      
out_z.write("/FUNCT/1000003\nmovz\n")   
  
# for row in reader:
  # print(row)
  # print (row[0], )
f = 1.0e-3
x = [float(data[1][0]), float(data[1][1]), float (data[1][2])]
xo = f * float (data[1][0])
yo = f * float (data[1][1])
zo = f * float (data[1][2])

print ("First Point: ", x)

avg_d = 0.0
  
t = 0.0  

out_x.write(writeFloatField(t*60.0,20,10) + writeFloatField(0.0,20,10) + "\n")
out_y.write(writeFloatField(t*60.0,20,10) + writeFloatField(0.0,20,10) + "\n")
out_z.write(writeFloatField(t*60.0,20,10) + writeFloatField(0.0,20,10) + "\n")

out_x.write(writeFloatField(t_interf,20,10) + writeFloatField(0.0,20,10) + "\n")
out_y.write(writeFloatField(t_interf,20,10) + writeFloatField(0.0,20,10) + "\n")
out_z.write(writeFloatField(t_interf,20,10) + writeFloatField(zo-thck/2.0, 20,10) + "\n")


for i in range (2, len(data)) :
  xp = np.array(data[i-1])
  # x = np.array(data[i])
  # x = np.array([float(data[i][0]), float(data[i][1]), float (data[i][2])])
  x = np.array([float(data[i][0]), float(data[i][1]), float (data[i][2])])
  xp = np.array([float(data[i-1][0]), float(data[i-1][1]), float (data[i-1][2])])
  # xp = data[i-1]
  lst1 = [10,20,30,40,50]
  dist = np.linalg.norm(x-xp)
  avg_d = avg_d + dist
  v = x -xp
  # print ("x xp v dist", x, xp, v, dist)
  # print ("norm" )
  # print (i, data[i][0], data[i][1] ,data[i][2])
  print (i, x[0], x[1] ,x[2])
  if (dist > 1.0e-5):
    #dt = dist/vel
    t = t + dt

    out_x.write(writeFloatField(t*60.0+t_interf,20,10) + writeFloatField(f*x[0] - xo,20,10) + "\n")
    out_y.write(writeFloatField(t*60.0+t_interf,20,10) + writeFloatField(f*x[1] - yo,20,10) + "\n")
    out_z.write(writeFloatField(t*60.0+t_interf,20,10) + writeFloatField(f*x[2]-thck/2.0,20,10) + "\n")
  else:
    print("ERROR, POINT DISTANCE LESS THAN 1E-5")
  
t +=10.0*dt
out_x.write(writeFloatField(t*60.0+t_interf,20,10) + writeFloatField(f*x[0] - xo, 20,10) + "\n")
out_y.write(writeFloatField(t*60.0+t_interf,20,10) + writeFloatField(f*x[1] - yo, 20,10) + "\n")
out_z.write(writeFloatField(t*60.0+t_interf,20,10) + writeFloatField(0.0,20,10) + "\n")
    
# The type of file is “_io.TextIOWrapper” which is a file object that is returned by the open()
# type(file)
avg_d = avg_d/pt_count
print ("Avg distance: ", avg_d)
out_x.close,out_y.close,out_z.close
