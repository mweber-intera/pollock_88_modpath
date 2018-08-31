import flopy
import pandas as pd
import numpy as np
import os

model_ws = os.path.join('workspace')
# ymax
# step 1: identify maximum y value from endpoint pathfile

endpoint = os.path.join('workspace','test_case_3.mpend')
pathline = os.path.join('workspace','test_case_3.mppth')

well_x = 31025
well_y = 9975

well_x = 53350 + 25
well_y = 19950 + 25



with open(os.path.join('workspace','test_case_3.mpend'), 'r') as f:
    lines_after_header = f.readlines()[6:]
    step = []
    for line in lines_after_header:
        step.append(line.split()[27])
floaty = [float(x) for x in step]
maxy = max(floaty)
mymax = maxy-well_y
miny = min(floaty)
mymin = miny-well_y


# step 2: calculate difference between ymax and mymax
import fetter
Qgpm = 100
Qcfd = Qgpm * (60*24) / 7.48052
b = 175.25
hk = 1000
h1, h2 = 200, 199.048
L = 80000
grad = (h2 - h1)/(L)
ymax = fetter.ymax_uc(Qcfd,hk,h1,h2,L)

percent_difference_ymax = ((ymax - mymax)/((ymax+mymax)/2))*100

percent_difference_ymin = (((0-ymax) - mymin)/(((0-ymax)+mymin)/2))*100


# stagnation point
# step 1: identify maximum x value from pathline file
with open(os.path.join('workspace','test_case_3.mppth'), 'r') as f:
    lines_after_header = f.readlines()[3:]
    step = []
    for line in lines_after_header:
        step.append(line.split()[5])
floatx = [float(x) for x in step]
# print(floatx)
maxx = max(floatx)
# print(maxx)
mmaxx =maxx-well_x
# print(mmaxx)


# step 2: calculate difference between ymax and mymax

def stag_dist_uc(Qcfd,L,hk,h1,h2):
    return (-Qcfd*L)/(np.pi*hk*(((h1**2)-(h2**2))))

xstag=-stag_dist_uc(Qcfd,L,hk,h1,h2)
percent_difference_xstag = ((xstag - mmaxx)/((xstag+mmaxx)/2))*100



# checking points along the curve
# step 1: pull y values from pathline file
with open(os.path.join('workspace','test_case_3.mppth'), 'r') as f:
    lines_after_header = f.readlines()[3:]
    step = []
    for line in lines_after_header:
        step.append(line.split()[6])
mp_y = [float(x) for x in step]

#print(mp_y)

# pull modpath x
with open(os.path.join('workspace','test_case_3.mppth'), 'r') as f:
    lines_after_header2 = f.readlines()[3:]
    step2 = []
    for line in lines_after_header2:
        step2.append(line.split()[5])
mp_x = [float(x) for x in step2]

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

loc_y=[]
loc_y1=[loc_y.append(i-well_y) for i in mp_y]


perd=[]
pd1=[perd.append(((c_list[i] - loc_x[i])/(c_list[i]+loc_x[i]/2))*100) for i in range(0,len(c_list))]

# define pass/fail criteria
if abs(percent_difference_xstag) > 20:
    xstag_pf = 'Fail'
else:
    xstag_pf = 'Pass'

if abs(percent_difference_ymax) > 20:
    ymax_pf = 'Fail'
else:
    ymax_pf = 'Pass'

if abs(percent_difference_ymin) > 20:
    ymin_pf = 'Fail'
else:
    ymin_pf = 'Pass'

outpath = 'output'
if not os.path.exists(outpath): os.mkdir(os.path.join(outpath))


dictionary2 = {'analytical_xstag':xstag, 'modpath_xstag':mmaxx, 'Percent_difference_xstag':percent_difference_xstag,
               'Xstag_Status':xstag_pf, 'analytical_ymax':ymax, 'modpath_ymax':mymax,
               'Percent_difference_ymax':percent_difference_ymax, 'Ymax_Status':ymax_pf,
               'modpath_ymin':mymin, 'Percent_difference_ymin':percent_difference_ymin, 'Ymin_Status':ymin_pf}
output2=pd.DataFrame(dictionary2, index=[0])


out_csv2 = 'tc3_results.csv'
output2.to_csv(os.path.join(outpath, out_csv2),index=False)

