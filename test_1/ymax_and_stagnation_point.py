import flopy
import pandas as pd
import numpy as np
import os

model_ws = os.path.join('workspace')

# ymax
# step 1: identify maximum y value from endpoint pathfile

endpoint = os.path.join('workspace','test_1.mpend')
pathline = os.path.join('workspace','test_1.mppth')

well_x = 31005
well_y = 9995


with open(os.path.join('workspace','test_1.mpend'), 'r') as f:
    lines_after_header = f.readlines()[6:]
    step = []
    for line in lines_after_header:
        step.append(line.split()[27])
floaty = [float(x) for x in step]
print(floaty)
maxy = max(floaty)
print(maxy)
mymax = maxy-well_y
print(mymax)


# step 2: calculate difference between ymax and mymax
import fetter
Qgpm = 2.5
Qcfd = Qgpm * (60*24) / 7.48052
b = 175.25
hk = 10
h1, h2 = 200, 167.35
L = 40000
grad = (167.35-200)/(40000)
ymax = fetter.ymax_uc(Qcfd,hk,h1,h2,L)

percent_difference = ((abs(ymax) - abs(mymax))/((abs(ymax)+abs(mymax))/2))*100
print(percent_difference)

# stagnation point
# step 1: identify maximum x value from pathline file
with open(os.path.join('workspace','test_1.mppth'), 'r') as f:
    lines_after_header = f.readlines()[3:]
    step = []
    for line in lines_after_header:
        step.append(line.split()[5])
floatx = [float(x) for x in step]
print(floatx)
maxx = max(floatx)
print(maxx)
mmaxx = maxx-well_x
print(mmaxx)


# step 2: calculate difference between ymax and mymax
Qgpm = 2.5
Qcfd = Qgpm * (60*24) / 7.48052
hk = 10
h1, h2 = 200, 167.35
L = 40000

def stag_dist_uc(Qcfd,L,hk,h1,h2):
    return (Qcfd*L)/(np.pi*hk*(((h2**2)-(h1**2))))

xstag=stag_dist_uc(Qcfd,L,hk,h1,h2)
print(xstag)
percent_difference = ((xstag - mmaxx)/(xstag+(mmaxx))) *100
print(percent_difference)

# # checking points along the curve
# # step 1: pull y values from pathline file
# with open(os.path.join('workspace','test_1.mppth'), 'r') as f:
#     lines_after_header = f.readlines()[4:]
#     step = []
#     for line in lines_after_header:
#         step.append(line.split()[5])
# floatys = [float(x) for x in step]
# print(floatys)
#
# # step 2: plug modpath x values into make_shape_uc
# def make_shape_uc(y,Q,k,h1,h2,L):
#     x = -y/ np.tan((np.pi*k*((h2**2)-(h1**2))*y)/(Q*L))
#     return x
#
# for y in floatys:
#     calcx = make_shape_uc(y=floatys,Q,k,h1,h2,L)
#     print(calcx)

# should probably write that to a csv as well
# should probably set it up such that it gives you a wrong number when you have the wrong sign
# nah, all points are reaching the well, so don't worry about it
