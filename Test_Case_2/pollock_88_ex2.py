import flopy
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd


modelname = 'test_2'
exe = os.path.join("..","gw_codes",'mf2k-chprc08spl.exe')
model_ws = os.path.join('workspace')
mf = flopy.modflow.Modflow(modelname, version='mf2k', exe_name =exe,model_ws=model_ws)

# DIS
nlay = 1 # number of layers
nrow, ncol = 11,21 # number of rows and columns
top = np.ones((nrow,ncol)) * 25 # 2d array of size (nrow * ncol) * 100
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


# LPF
hk = np.ones((nlay,nrow,ncol)) * 45
hk[0][0,:10] = 4500
hk[0][5,11:ncol] = 4500
lpf = flopy.modflow.ModflowLpf(mf,hk=hk,ipakcb=53)

# BAS
ibound = np.ones((nlay,nrow,ncol))
ibound[0][0:5, 10:] = 0
ibound[0][0:9, 10] = 0
strt = np.ones((nlay,nrow,ncol)) * 55
strt[:,11:] = 25
bas = flopy.modflow.ModflowBas(mf, ibound=ibound, strt=strt) # create bas object, all cells are active, starting head = 100 ft

# OC
spd = {} # initialize spd for oc
for i in range(dis.nper):
    spd[(i, 0)] = ['save head', 'save budget']
oc = flopy.modflow.ModflowOc(mf, stress_period_data=spd, compact=True) # compact = True to use in modpath later

# CHD
lrcd = {0:[]}
cols = np.arange(0,10)
for c in cols:
    lrcd[0].append([0,0,c,55,55])

cols = np.arange(11,ncol)
for c in cols:
    lrcd[0].append([0,5,c,25,25])
print(lrcd)
chd = flopy.modflow.ModflowChd(mf, stress_period_data=lrcd)

#PCG
#I've seen examples of all three solvers being used
pcg = flopy.modflow.ModflowPcg(mf)

mf.write_input() # write modflow files
success, buff = mf.run_model(silent=False)



#modpath

mpexe = os.path.join("..","gw_codes",'mp6.exe')

mp = flopy.modpath.Modpath('test_2',exe_name=mpexe,modflowmodel=mf,model_ws=model_ws,dis_file = mf.name+'.dis',head_file=mf.name+'.hds',budget_file=mf.name+'.cbc')

mp_ibound = mf.bas6.ibound.array # use ibound from modflow model
mpb = flopy.modpath.ModpathBas(mp,-1e30,ibound=mp_ibound,prsity=.3) # make modpath bas object

start_time=[0]

import Write_starting_locations
srt_loc = 'starting_locs_ex2.loc'
Write_starting_locations.write_file_ex2(os.path.join(model_ws,srt_loc),dis,start_time,10*4) # custom function in Write_starting_locations.py

sim = mp.create_mpsim(trackdir='forward', simtype='pathline', packages=srt_loc, start_time=(0, 0, 0)) # create simulation file

# sim.time_ct = 10
# time_pts =[]
# for tp in range(sim.time_ct):
    # time_pts.append(tp*2.18)
#
# sim.time_pts = time_pts

mp.write_input() # write files

mp.run_model(silent=False) # run model

outpath = os.path.join('output')
if not os.path.exists(outpath): os.mkdir(outpath)
figures = os.path.join('output','figures')
if not os.path.exists(figures): os.mkdir(figures)

import flopy.utils.binaryfile as bf

headobj = bf.HeadFile(os.path.join(model_ws,'test_2.hds')) # make head object with hds file
times = [0] + headobj.get_times() # get the times
print(times)

pthobj = flopy.utils.PathlineFile(os.path.join(model_ws,'test_2.mppth')) # create pathline object
epdobj = flopy.utils.EndpointFile(os.path.join(model_ws,'test_2.mpend')) # create endpoint object

fig_list = [] # initialize list of figure paths we will use to make a gif
for time in times:
    fig, ax = plt.subplots(figsize=(8,5))
    extent=(0,Lx,0,Ly)
    if time != 0:
        head = headobj.get_data(totim=time)
        # CS = plt.contour(np.flipud(head[0]), extent=extent, color='k',vmin=0,vmax=55)
        # plt.clabel(CS, inline=1, fontsize=10)
        plt.imshow(head[0],cmap='jet',extent=extent,vmin=0)
    else:
        plt.imshow(np.ones((nrow,ncol)),cmap='jet',extent=extent)
        # plt.colorbar()

    modelmap = flopy.plot.ModelMap(model=mf, layer=0, ax=ax)
    lc = modelmap.plot_grid(color='c',alpha=.25)
    qm = modelmap.plot_bc('CHD', alpha=0.5)
    ib = modelmap.plot_ibound()

    well_epd = epdobj.get_alldata()
    well_pathlines = pthobj.get_alldata()
    modelmap.plot_pathline(well_pathlines, travel_time=f'<={time}', layer='all', colors='red') # plot pathline <= time
    modelmap.plot_endpoint(well_epd, direction='starting', colorbar=False) # can only plot starting of ending, not as dynamic as pathlines
    fig_name = os.path.join(figures,f'{str(round(time,2)).replace(".","pt")}_days.png') # figure path to save to
    fig.text(0.15, .95,
             f'Day = {round(time,3)}',
             fontsize=16, color='k',
             ha='left', va='bottom', alpha=1)
    plt.title('Pollock 1988 Ex. 2')
    fig.tight_layout()
    fig.savefig(fig_name)
    plt.close()





# names = ['Time_Point_Index','Cumulative_Time_Step','Tracking_Time','Particle_ID','Particle_Group','Global_X','Global_Y',
#          'Global_Z','Grid','Layer','Row','Column','Local_X','Local_Y','Local_Z']
# ts_df = pd.read_csv(os.path.join(model_ws,'test_2.mp.tim_ser'),skiprows=3,names = names,delim_whitespace=True)
# print(ts_df.loc[ts_df['Particle_ID']==1])
# fig_list = [] # initialize list of figure paths we will use to make a gif
# for time in time_pts:
#     fig, ax = plt.subplots(figsize=(8,5))
#     extent=(0,Lx,0,Ly)

#     modelmap = flopy.plot.ModelMap(model=mf, layer=0, ax=ax)
#     lc = modelmap.plot_grid(color='c',alpha=.25)
#     qm = modelmap.plot_bc('CHD', alpha=0.5)
#     ib = modelmap.plot_ibound()

#     # well_epd = epdobj.get_alldata()
#     # well_pathlines = pthobj.get_alldata()
#     # modelmap.plot_pathline(well_pathlines, travel_time=f'<={time}', layer='all', colors='red') # plot pathline <= time
#     # modelmap.plot_endpoint(well_epd, direction='starting', colorbar=False) # can only plot starting of ending, not as dynamic as pathlines
#     tempdf = ts_df.loc[(ts_df['Tracking_Time'] >= time-.5) & (ts_df['Tracking_Time'] <= time+.5)]
#     ax.scatter(tempdf['Global_X'],tempdf['Global_Y'])
#     fig_name = os.path.join(figures,f'1c_{str(round(time,2)).replace(".","pt")}_days.png') # figure path to save to
#     fig.text(0.15, 0.85,
#              f'Day = {str(round(time,3))}',
#              fontsize=16, color='k',
#              ha='left', va='bottom', alpha=1)
#     plt.title('Pollock 1988 Ex. 2')
#     ax.set_ylim([0,10])
#     ax.set_xlim([0,10])
#     fig.tight_layout()
#     fig.savefig(fig_name)
#     plt.close()

plt.close('all')