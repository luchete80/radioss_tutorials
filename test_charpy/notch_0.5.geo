//GMSH project
mm = 1.0e-3;
h  = 10.0 * mm;
hn =  2.0 * mm;
r = 0.3 * mm;
hdiv = 7.0 *mm;
ltot = 25.0 *mm; 

lc = 2.5e-4;
ls = 1.0e-3; //Sparse
thck = 10.0*mm;

a = 45.0 * Pi / 180.0;
ca = Cos(a); sa = Sin(a);

p1y = h - hn + r;
hyp =  Hypot(h - p1y,-r*sa);

xn = r*sa + hyp *sa;
 
Point(1)  = {0.0,p1y,0.0,lc}; 
Point(2)  = {-r*sa,p1y - r*ca,0.0,lc};  Point(3)  = {r*sa,p1y - r*ca,0.0,lc};    
Circle(1) = {2, 1, 3};  
Point(4)  = {-xn,h,0.0,lc};      Point(5)  = {xn,h,0.0,lc};                         
Line(2) = {4,2}; Line(3) = {5,3};

Point(6)  = {-xn,hdiv, 0.0,lc};
Point(7)  = {xn,hdiv, 0.0,lc};

Point(8)  = {-xn,0.0,0.0,ls}; Point(9)  = {xn,0.0,0.0,ls};

Point(10)  = {-r*sa,hdiv,0.0,lc}; Point(11)  = {r*sa,hdiv,0.0,lc};
Point(12)  = {-r*sa,0.0,0.0,ls}; Point(13)  = {r*sa,0.0,0.0,ls}; //Bottom

Line(4) = {4,6}; Line(5) = {5,7};
Line(6) = {6,10}; Line(7) = {10,11}; Line(8) = {11,7};
Line(9) = {6,8}; Line(10) = {7,9};
Line(11) = {12,13};
Line(12) = {2,10}; Line(13) = {3,11};
Curve Loop(1) = {4,6,-12,-2}; Curve Loop(2) = {-5,3,13,8};

Curve Loop(3) = {7,-13,-1,12};

Line(14) = {8,12};Line(15) = {13,9};
Line(16) = {10,12};Line(17) = {11,13};

//Curve Loop(1) = {6,-5,3,-1,-2,4};
Surface(1) = {1}; Surface(2) = {2};
Surface(3) = {3};

Curve Loop(4) = {9,14,-16,-6}; Curve Loop(5) = {17,15,-10,-8}; 
Surface(4) = {4}; Surface(5) = {5};

Curve Loop(6) = {16,11,-17,-7};
Surface(6) = {6};

//Limits
Point(14)  = {-ltot,h, 0.0,ls};Point(15)  = {ltot,h, 0.0,ls};
Point(16)  = {-ltot,0.0, 0.0,ls};Point(17)  = {ltot,0.0, 0.0,ls};
Line (18) = {14,4}; Line (19) = {5,15};
Line (20) ={14,16}; Line(21) ={15,17};
Line (22) = {16,8}; Line (23) = {9,17};
Curve Loop (7) = {20,22,-9,-4,-18}; Curve Loop(8) = {10,23,-21,-19,5};
Plane Surface(7) = {7}; Plane Surface(8) = {8};


Recombine Surface "*";

Extrude {0,0,thck} {Surface{1,2,3}; Layers{10};Recombine;}
Extrude {0,0,thck} {Surface{4,5,6}; Layers{10};Recombine;}
Extrude {0,0,thck} {Surface{7,8}; Layers{10};Recombine;}




