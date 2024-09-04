# What is Radioss Incforming? 
Is a python script to generate input files to solve incremental forming process in [Radios] (https://github.com/OpenRadioss/OpenRadioss) solver.

![ScreenShot](https://github.com/luchete80/radioss_incforming/blob/master/screenshot.png)
## How to use it?
0. If you have the toolpath as CSV file andyou wish to import it, run:
```
python convert_csv.py 
```
This scrip generates mov[i/o]_z.inc which are included in radioss starter file.

1. Run the script
```
python asdif_gen.py 
```
The files "test_000X.rad" will be generated. Once it is done, 

2. exectute Radioss starter to generate engine input:
```
starter_win64 -i test_0000.rad
```

3. Run Radioss Engine:
```
engine_win64 -i test_0001.rad
```

4. Converto outputs to vtk
```
anim_to_vtk__win64 testAXXX > test.vtk
```


5. Post process tool force
```
python tool_force.py
```



## Types of Models
By changing ```cont_support ``` inside the script, the model has shell boundaries fixed either by nodal fixities (```cont_support = False```) or by contact. 

The functions for the master node groups in the spheres 

Also, the rotations are fixed for each node group representing the sphere masters:
```
  BoundSpcSet_1 
  #  Tra rot   skew_ID  grnod_ID
  000 111         0       102
``` 
   
In the case of using Contact in the supports, a node group is created, then a RBODY and 
finally a GRNOD FOR THE MASTER SURFACE, IN WHICH A BCS IS CREATED

## Interfaces
```
/INTER/TYPE7/inter_ID/unit_ID
inter_title
grnd_IDs	surf_IDm

grnd_IDs	Secondary nodes group identifier.
(Integer)
surf_IDm	Main surface identifier.
(Integer)
```

For each interfaces, we have the master surface ID being the SURFACE ID(defined for example "/SURF/PART/1000002").
The first two interfaces corresponds to each ball-shell side, whereas the followings are used 
in the case of contact between plate and support

```
/INTER/TYPE7/4
INTERFACE 4
#  Slav_id   Mast_id      Istf      Ithe      Igap                Ibag      Idel     Icurv      Iadm
         1   1000006         0         0         0                   0         0         0         0
```

Things to add for Damping and MS
```
/DAMP/1
MASS_DAMP_1
100.0                                   1
/AMS
1
/GRPART/PART/1
PART_1
1
```
And, in engine file
```
/DT/AMS/0
0.67
```

Too see examples with contact heating
https://2021.help.altair.com/2021/hwsolvers/rad/topics/solvers/rad/thermal_analysis_example_r.htm

