import flopy
import os
import numpy as np
import matplotlib.pyplot as plt
import platform

model_ws = os.path.join('pollock_model_ex1')
if not os.path.exists(model_ws): os.mkdir(model_ws)
gw_codes = os.path.join('gw_codes')
exe = os.path.join(gw_codes,'mfnwt.exe')
if platform.system() == 'Darwin':
    exe = 'mfnwt' # assuming you have mfnwt in your path
mf = flopy.modflow.Modflow('pollock_88',version='mfnwt',exe_name=exe,model_ws=model_ws)



nlay = 1
nrow, ncol = 81,81
top = np.ones((nrow,ncol)) * 100
botm = np.ones((nlay,nrow,ncol)) * 0
delr, delc = 100, 100

nper = 15
perlen = [500]
steady = [False]
nstp = [1]
for sp in range(0,nper-1):
    perlen.append(500)
    steady.append(False)
    nstp.append(1)
laycbd = 0


dis = flopy.modflow.ModflowDis(mf,nlay,nrow,ncol,nper,delr,delc,0,top,botm,perlen,nstp,1,steady)

upw = flopy.modflow.ModflowUpw(mf,hk=10,ipakcb=53)

bas = flopy.modflow.ModflowBas(mf, ibound=1, strt=100.0)

spd = {}
for i in range(dis.nper):
    spd[(i, 0)] = ['save head', 'save budget']
oc = flopy.modflow.ModflowOc(mf, stress_period_data=spd, compact=True)

nwt = flopy.modflow.ModflowNwt(mf, maxiterout=5000, linmeth=2, iprnwt=1)

Qcfd = 160000.
wel_spd = {}
for sp in range(nper):
    wel_spd[sp] = [0,int(nrow/2),int(ncol/2),Qcfd]

print(wel_spd)
wel = flopy.modflow.ModflowWel(mf,stress_period_data=wel_spd)


def PointsInCircum(x,y, r,n=8):
    a = [[np.cos(2*np.pi/n*i)*r,np.sin(2*np.pi/n*i)*r] for i in range(0,n+1)]
    x0 = np.array([i[0] for i in a])
    y0 = np.array([i[1] for i in a])
    return x0+x, y0+y

Lx, Ly = delr*ncol, delc*nrow
x,y = Lx/2, Ly/2

def createCircularMask(h, w, center=None, radius=None):
    if center is None: # use the middle of the image
        center = [int(w/2), int(h/2)]
    if radius is None: # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    mask = (dist_from_center < radius+1) & (dist_from_center >= radius)
    return mask

mask = createCircularMask(ncol,nrow,radius=40)
chd_locsX, chd_locsY = np.where(mask)[0], np.where(mask)[1]
chd_dat = []
for i in range(len(chd_locsX)):
    cx,cy = chd_locsX[i], chd_locsY[i]
    chd_dat.append([0,cx,cy,100,100])

chd_spd = {0:chd_dat}
chd = flopy.modflow.ModflowChd(mf,stress_period_data=chd_spd)


mf.write_input()
mf.run_model()




# now for modpath

mpexe = os.path.join(gw_codes,'mp6.exe')
if platform.system() == 'Darwin':
    mpexe = 'mp6' # assuming you have mp6 in your path

mp = flopy.modpath.Modpath('pollock_88_mp',exe_name=mpexe,modflowmodel=mf,model_ws=model_ws,dis_file = mf.name+'.dis',head_file=mf.name+'.hds',budget_file=mf.name+'.cbc')

mp_ibound = np.zeros((nrow,ncol))
mp_ibound[int(nrow/2),int(ncol/2)] = 1
mpb = flopy.modpath.ModpathBas(mp,upw.hdry,ibound=mp_ibound,prsity=.3)

start_time=[0]

import Write_starting_locations
srt_loc = 'starting_locs.loc'
Write_starting_locations.write_file(os.path.join(model_ws,srt_loc),dis,start_time,10*4)

sim = mp.create_mpsim(trackdir='forward', simtype='pathline', packages=srt_loc, start_time=(0, 0, 0))
mp.write_input()

mp.run_model(silent=False)



import flopy.utils.binaryfile as bf

headobj = bf.HeadFile(os.path.join(model_ws,'pollock_88.hds'))
times = headobj.get_times()
print(times)

pthobj = flopy.utils.PathlineFile(os.path.join(model_ws,'pollock_88_mp.mppth'))
epdobj = flopy.utils.EndpointFile(os.path.join(model_ws,'pollock_88_mp.mpend'))


head = headobj.get_data(totim=times[-1])
fig, ax = plt.subplots()
# plt.colorbar()
# ax.scatter(X_chd, Y_chd)

extent=(0,Lx,0,Ly)
CS = plt.contour(np.flipud(head[0]), extent=extent, color='k')
modelmap = flopy.plot.ModelMap(model=mf, layer=0, ax=ax)
lc = modelmap.plot_grid(alpha=.25)
qm = modelmap.plot_bc('CHD', alpha=0.5)
plt.clabel(CS, inline=1, fontsize=10)
# plt.imshow(head[0],cmap='cubehelix',extent=extent)
# plt.colorbar()

well_epd = epdobj.get_alldata()
well_pathlines = pthobj.get_alldata()
modelmap.plot_pathline(well_pathlines, travel_time='<10000', layer='all', colors='red')
modelmap.plot_endpoint(well_epd, direction='starting', colorbar=False)

plt.show()