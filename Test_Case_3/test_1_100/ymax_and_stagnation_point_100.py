import flopy
import pandas as pd
import numpy as np
import os

model_ws = os.path.join('workspace')

# ymax
# step 1: identify maximum y value from endpoint pathfile

endpoint = os.path.join('workspace','test_1.mpend')
pathline = os.path.join('workspace','test_1.mppth')

well_x = 31050
well_y = 19950


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
# Qgpm = 2.5
# Qcfd = Qgpm * (60*24) / 7.48052
Qcfd = 1000
b = 175.25
hk = 10
h1, h2 = 200, 167.35
L = 40000
grad = (167.35-200)/(40000)
ymax = fetter.ymax_uc(Qcfd,hk,h1,h2,L)

percent_difference_ymax = ((ymax - mymax)/((ymax+mymax)/2))*100
print(percent_difference_ymax)

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

def stag_dist_uc(Qcfd,L,hk,h1,h2):
    return (-Qcfd*L)/(np.pi*hk*(((h1**2)-(h2**2))))

xstag=-stag_dist_uc(Qcfd,L,hk,h1,h2)
print(xstag)
percent_difference_xstag = ((xstag - mmaxx)/((xstag+mmaxx)/2))*100
print(percent_difference_xstag)



# checking points along the curve
# step 1: pull y values from pathline file
with open(os.path.join('workspace','test_1.mppth'), 'r') as f:
    lines_after_header = f.readlines()[3:]
    step = []
    for line in lines_after_header:
        step.append(line.split()[6])
mp_y = [float(x) for x in step]
print(mp_y)

#print(mp_y)

# pull modpath x
with open(os.path.join('workspace','test_1.mppth'), 'r') as f:
    lines_after_header2 = f.readlines()[3:]
    step2 = []
    for line in lines_after_header2:
        step2.append(line.split()[5])
mp_x = [float(x) for x in step2]
print(mp_x)

# step 2: plug modpath x values into make_shape_uc
def make_shape_uc(y,Qcfd,hk,h1,h2,L):
    x = -y/ np.tan((np.pi*hk*((h1**2)-(h2**2))*y)/(Qcfd*L))
    return x

c_list = []
for i in range(len(mp_y)):
    y=(mp_y[i]-well_y)
    calcx = -make_shape_uc(y,Qcfd,hk,h1,h2,L)
    c_list.append(calcx)


loc_x=[]
loc_x1=[loc_x.append(i-well_x) for i in mp_x]
print(loc_x)

loc_y=[]
loc_y1=[loc_y.append(i-well_y) for i in mp_y]
print(loc_y)
print(mp_y)

perd=[]
pd1=[perd.append(((c_list[i] - loc_x[i])/(c_list[i]+loc_x[i]/2))*100) for i in range(0,len(c_list))]
print(perd)

dictionary = {'analytical_local_x':c_list, 'modpath_local_x':loc_x, 'modpath_local_y':loc_y, 'modpath_global_x':mp_x, 'modpath_global_y':mp_y, 'percent_difference':perd}
output=pd.DataFrame(dictionary)
print(output)
out_csv = 'percent_diff_shape.csv'
output.to_csv(out_csv)

dictionary2 = {'analytical_xstag':xstag, 'modpath_xstag':mmaxx, 'Percent_difference_xstag':percent_difference_xstag, 'analytical_ymax':ymax, 'modpath_ymax':mymax, 'Percent_difference_ymax':percent_difference_ymax}
output2=pd.DataFrame(dictionary2, index=[0])
print(dictionary2)
out_csv2 = 'percent_diff_ymax_xstag.csv'
output2.to_csv(out_csv2)

# should probably write that to a csv as well
# should probably set it up such that it gives you a wrong number when you have the wrong sign
# nah, all points are reaching the well, so don't worry about it
