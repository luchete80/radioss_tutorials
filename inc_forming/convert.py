from convert_in_csv  import *
from convert_out_csv import *
import sys

# total arguments
n = len(sys.argv)

#for i in range(1, n):
#  print(sys.argv[i], end = " ")

if (sys.argv[2]=="Top"):
  print("Converting Top Tool..")
  convert_in(sys.argv[1])
else:
  if (sys.argv[2]=="Bot"):
    print("Converting Bot Tool..")
    convert_out(sys.argv[1])
  else:
    print("Wrong arguments. Usage: convert <file.csv> <Top/Bottom>")
