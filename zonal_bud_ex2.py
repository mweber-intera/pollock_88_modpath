import flopy
import os
import numpy as np
import matplotlib.pyplot as plt
import platform
import imageio



model_ws = os.path.join('pollock_model_ex2')
if not os.path.exists(model_ws): os.mkdir(model_ws)
gw_codes = os.path.join('gw_codes')
exe = os.path.join(gw_codes,'mfnwt.exe')
if platform.system() == 'Darwin':
    exe = 'mfnwt' # assuming you have mfnwt in your path
mf = flopy.modflow.Modflow.load('pollock_88_ex2.nam',version='mfnwt',exe_name=exe,model_ws=model_ws,load_only=['dis'])
dis = mf.dis
nlay, nrow, ncol = dis.nlay, dis.nrow, dis.ncol
delr, delc = dis.delr.array, dis.delc.array
thicknes = dis.thickness.array
# make a zonal budget text file
# start with making an array of size nrow * ncol
zb = np.ones((nrow,ncol))
zb[9,0] = 2 # cell (10,1)
zb[10,0] = 3 # (11, 1) <- bottom left corner
zb[10,1] = 4 # (11,2)
fig, ax = plt.subplots()
plt.imshow(zb)
plt.colorbar()
plt.title('Zones')

np.savetxt(os.path.join(model_ws,'1.zon'),zb,fmt='%1.0f',delimiter=' ')
content = []
with open(os.path.join(model_ws, '1.zon')) as f:
    n1 = (f.readlines())
    for c in range(0, len(n1)):
        content.append(n1[c])
content[-1].replace('\n','')

zone_file = os.path.join(model_ws, 'zonef_mlt.zbr')
with open(zone_file,'w') as f:
    f.write(f'{nlay} {nrow} {ncol}\n')
    f.write(f'INTERNAL	({ncol}I2)\n')
    for i in range(0, len(content)):
        f.write(content[i])
    f.close()

import flopy.utils.binaryfile as bf
from flopy.utils.zonbud import ZoneBudget, read_zbarray
cbcobj = bf.CellBudgetFile(os.path.join(model_ws,mf.name+'.cbc'))

aliases = {1: 'Other', 2:'Top', 3: 'Corner', 4:'Right'}
zonal = read_zbarray(zone_file)
zb_DF = ZoneBudget(os.path.join(model_ws,mf.name+'.cbc'),zonal,aliases=aliases,kstpkper=cbcobj.get_kstpkper())

import pandas as pd
zb_DF = pd.DataFrame(zb_DF.get_dataframes())
zb_DF.reset_index(inplace=True)

print(zb_DF.head())
zb_DF.to_csv(os.path.join(model_ws,'zonal_budget.csv'))



# now lets calculate velocity into and out of the corner!

times = zb_DF['totim'].unique().tolist()
from_top = zb_DF.loc[zb_DF['name'] == 'FROM_Top']
# currently in cf-day, divide by cross sectional area to get velocity
b = thicknes[0][10,0]
n = .3
print(f'thicknes = {b}, delr = {delr[0]}')
from_top['Corner_fpd'] = from_top['Corner'] / ((delr[0]*b) * n)
print(from_top.head())



plt.show()