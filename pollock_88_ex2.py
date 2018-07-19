import flopy
import os
import numpy as np
import matplotlib.pyplot as plt
import platform
import imageio
import pandas as pd # pandas is a package that is used to work with dataframes (stolen from the R language) this will be
# how we import csv files


model_ws = os.path.join('pollock_model_ex2')
if not os.path.exists(model_ws): os.mkdir(model_ws)
gw_codes = os.path.join('gw_codes')
exe = os.path.join(gw_codes,'mfnwt.exe')
if platform.system() == 'Darwin':
    exe = 'mfnwt' # assuming you have mfnwt in your path
mf = flopy.modflow.Modflow('pollock_88_ex2',version='mfnwt',exe_name=exe,model_ws=model_ws)

nlay = 1 # number of layers
nrow, ncol = 11,21 # number of rows and columns
top = np.ones((nrow,ncol)) * 5 # 2d array of size (nrow * ncol) * 100
botm = np.ones((nlay,nrow,ncol)) * 0 # 2d array of size (nrow * ncol) * 0
delr, delc = 5, 5 # height and width of each cell
Lx, Ly = delr*ncol, delc*nrow # model width and height in ft

nper = 30 # number of stress periods
perlen = [1] # number time units in first stress period (this case 1 day)
steady = [True] # steady state or transient in first stress period
nstp = [1] # number of time steps in first stress period
for sp in range(0,nper-1):
    perlen.append(1) # number time units in each stress period
    steady.append(True) # steady state or transient in each stress period
    nstp.append(1) # number of time steps in each stress period
laycbd = 0

dis = flopy.modflow.ModflowDis(mf,nlay,nrow,ncol,nper,delr,delc,0,top,botm,perlen,nstp,1,steady) # create dis object

upw = flopy.modflow.ModflowUpw(mf,hk=45,ipakcb=53) # create upw object


ibound = np.ones((nlay,nrow,ncol))
ibound[0][0:5, 10:] = 0
ibound[0][0:9, 10] = 0
strt = np.ones((nlay,nrow,ncol)) * 55
strt[:,11:] = 25
bas = flopy.modflow.ModflowBas(mf, ibound=ibound, strt=55) # create bas object, all cells are active, starting head = 100 ft


spd = {} # initialize spd for oc
for i in range(dis.nper):
    spd[(i, 0)] = ['save head', 'save budget']
oc = flopy.modflow.ModflowOc(mf, stress_period_data=spd, compact=True) # compact = True to use in modpath later

''' Made some changes, with two for loops, that itterate the columns we want since both sets of chds are in 2 rows
#make a chb array, use it as a mask, make the ones we use as 1, make the ones we don't use 0
west = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
east = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
#lrcd = {0: [[0, 0, west, 55, 55], [0, 5, east, 25, 25]]}
lrcd = {0: [[0, 0, 0, 55, 55], [0, 0, 1, 55, 55], [0, 0, 2, 55, 55],
            [0, 0, 3, 55, 55], [0, 0, 4, 55, 55], [0, 0, 5, 55, 55],
            [0, 0, 6, 55, 55], [0, 0, 7, 55, 55], [0, 0, 8, 55, 55],
            [0, 0, 9, 55, 55], [0, 0, 10, 55, 55], [0, 0, 11, 55, 55],
            [0, 4, 10, 55, 55], [0, 4, 11, 55, 55], [0, 4, 12, 55, 55],
            [0, 4, 13, 55, 55], [0, 4, 14, 55, 55], [0, 4, 15, 55, 55],
            [0, 4, 16, 55, 55], [0, 4, 17, 55, 55],
            [0, 4, 18, 55, 55], [0, 4, 19, 55, 55], [0, 4, 20, 55, 55]]}
'''


#so i know the above is a nightmare, but I tried doing a range using a colon, I tried using variables, and it hated it both times
#also the above is only for stress period zero, but the flopy tutorial says that "if the number of lists is smaller
#than the number of stress periods, then the last list of chds will apply until the end of the simulation"
#obviously this needs to be checked

#chd_spd = {0: stress_period_data} # only need do do in the first stress period since modflow uses the previous stress period if there is nothing in the current stress period.
#print(chd_spd)

lrcd = {0:[]}
cols = np.arange(0,10)
for c in cols:
    lrcd[0].append([0,0,c,55,55])

cols = np.arange(11,ncol)
for c in cols:
    lrcd[0].append([0,5,c,25,25])
print(lrcd)
chd = flopy.modflow.ModflowChd(mf, stress_period_data=lrcd)



nwt = flopy.modflow.ModflowNwt(mf, maxiterout=5000, linmeth=2, iprnwt=1) # solver for modflow nwt


mf.write_input() # write modflow files
mf.run_model(silent=False) # run model

# exit()
#modpath time!

mpexe = os.path.join(gw_codes,'mp6.exe')
if platform.system() == 'Darwin':
    mpexe = 'mp6' # assuming you have mp6 in your path

mp = flopy.modpath.Modpath('test2',exe_name=mpexe,modflowmodel=mf,model_ws=model_ws,dis_file = mf.name+'.dis',head_file=mf.name+'.hds',budget_file=mf.name+'.cbc')

mp_ibound = mf.bas6.ibound.array # use ibound from modflow model
mpb = flopy.modpath.ModpathBas(mp,upw.hdry,ibound=mp_ibound,prsity=.3) # make modpath bas object

start_time=[0]

import Write_starting_locations # note to mary: edit this for test2
srt_loc = 'starting_locs_ex2.loc' # name starting locations file
Write_starting_locations.write_file_ex2(os.path.join(model_ws,srt_loc),dis,start_time,10*4) # custom function in Write_starting_locations.py

sim = mp.create_mpsim(trackdir='forward', simtype='pathline', packages=srt_loc, start_time=(0, 0, 0)) # create simulation file
mp.write_input() # write files

mp.run_model(silent=False) # run model



import flopy.utils.binaryfile as bf

headobj = bf.HeadFile(os.path.join(model_ws,'pollock_88_ex2.hds')) # make head object with hds file
times = [0] + headobj.get_times() # get the times (we made this in the begining with the dis)
print(times) # should be every 500 days, but I added "0" to the begging so we can see when there is no pumping

pthobj = flopy.utils.PathlineFile(os.path.join(model_ws,'test2.mppth')) # create pathline object
epdobj = flopy.utils.EndpointFile(os.path.join(model_ws,'test2.mpend')) # create endpoint object

fig_list = [] # initialize list of figure paths we will use to make a gif
for time in times:
    fig, ax = plt.subplots(figsize=(8,5))
    extent=(0,Lx,0,Ly)
    if time != 0:
        head = headobj.get_data(totim=times[-1])
        # CS = plt.contour(np.flipud(head[0]), extent=extent, color='k')
        # plt.clabel(CS, inline=1, fontsize=10)
        # plt.imshow(head[0],cmap='cubehelix',extent=extent)
        # plt.colorbar()

    modelmap = flopy.plot.ModelMap(model=mf, layer=0, ax=ax)
    lc = modelmap.plot_grid(color='c',alpha=.25)
    qm = modelmap.plot_bc('CHD', alpha=0.5)
    ib = modelmap.plot_ibound()

    well_epd = epdobj.get_alldata()
    well_pathlines = pthobj.get_alldata()
    modelmap.plot_pathline(well_pathlines, travel_time=f'<={time}', layer='all', colors='red') # plot pathline <= time
    modelmap.plot_endpoint(well_epd, direction='starting', colorbar=False) # can only plot starting of ending, not as dynamic as pathlines
    fig_name = os.path.join('figures_ex2',f'{int(time)}_days.png') # figure path to save to
    fig.text(0.15, 0.85,
             f'Day = {int(time)}',
             fontsize=16, color='k',
             ha='left', va='bottom', alpha=1)
    plt.title('Pollock 1988 Ex. 2')
    fig.tight_layout()
    fig.savefig(fig_name)
    fig_list.append(imageio.imread(fig_name)) # append imagio.imread() for each figure path
    plt.close()


imageio.mimsave(os.path.join('figures_ex2','final_gif.gif'),fig_list,duration=.5) # now save a gif of all the figures in fig_list