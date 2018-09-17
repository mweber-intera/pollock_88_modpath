import flopy
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


model_ws = os.path.join('workspace')
if not os.path.exists(model_ws): os.mkdir(model_ws)
gw_codes = os.path.join('gw_codes')
exe = "../gw_codes/mf2k-chprc08spl.exe"
mf = flopy.modflow.Modflow('test_case_1', version='mf2k', exe_name =exe,model_ws=model_ws)


# DIS
nlay = 1 # number of layers
nrow, ncol = 40,40 # number of rows and columns
top = np.ones((nrow,ncol)) * 100 # 2d array of size (nrow * ncol) * 100
botm = np.ones((nlay,nrow,ncol)) * 0 # 2d array of size (nrow * ncol) * 0
delr, delc = 100, 100 # hieght and width of each cell
Lx, Ly = delr*ncol, delc*nrow # model width and height in ft


nper = 15 # number of stress periods
perlen = [500] # number time unites in first stress period (this case 500 days)
steady = [True] # steady state or transient in first stress period
nstp = [1] # number of time steps in first stress period
for sp in range(0,nper-1):
    perlen.append(500) # number time units in each stress period
    steady.append(True) # steady state or transient in each stress period
    nstp.append(1) # number of time steps in each stress period
laycbd = 0

dis = flopy.modflow.ModflowDis(mf,nlay,nrow,ncol,nper,delr,delc,0,top,botm,perlen,nstp,1,steady) # create dis object

# BAS
ibound = np.zeros((nlay,nrow,ncol))
ibound[0][:int(nrow/2),int(ncol/2):] = 1
bas = flopy.modflow.ModflowBas(mf, ibound=1, strt=100.0) # create bas object, all cells are active, starting head = 100 ft

#LPF change hydraulic conductivity here
lpf = flopy.modflow.ModflowLpf(mf, hk=10, vka=10., ipakcb=53)

#PCG
pcg = flopy.modflow.ModflowPcg(mf)

# OC
spd = {} # initialize spd for oc
for i in range(dis.nper):
    spd[(i, 0)] = ['save head', 'save budget']
oc = flopy.modflow.ModflowOc(mf, stress_period_data=spd, compact=True) # compact = True to use in modpath later


# WEL
Qcfd = 160000./4 # Q cf-days
wel_spd = {} 
for sp in range(nper):
    wel_spd[sp] = [0,nrow-1,0,Qcfd] # injection well is in center of the model


wel = flopy.modflow.ModflowWel(mf,stress_period_data=wel_spd) # well package

# CHD
chd_df = pd.read_csv(os.path.join('preproccessing','chb_t1.csv')) # read in csv with pandas

chd_dat = []
for i, vals in chd_df.iterrows(): # fancy for loop that returns the index in i, and the values in vals
    row, col = vals # unpack row and col
    col = col  # shift col to the right 40 cells
    chd_dat.append([0,int(row),int(col),100,100])



chd_spd = {0:chd_dat} # only need do do in the first stress period since modflow uses the previous stress period if there is nothing in the current stress period.
chd = flopy.modflow.ModflowChd(mf,stress_period_data=chd_spd)

# write modflow files
mf.write_input()

# Run the MODFLOW model
mf.run_model()




# now for modpath

mpexe = "../gw_codes/mp6.exe"

mp = flopy.modpath.Modpath('test_case_1',exe_name=mpexe,modflowmodel=mf,model_ws=model_ws,dis_file = mf.name+'.dis',head_file=mf.name+'.hds',budget_file=mf.name+'.cbc')

mp_ibound = mf.bas6.ibound.array # use ibound from modflow model
mpb = flopy.modpath.ModpathBas(mp,-1e30,ibound=mp_ibound,prsity =.3) # make modpath bas object
start_time=[0]

import Write_starting_locations # this is a script I made that write the starting location file
srt_loc = 'starting_locs.loc' # name starting locations file
Write_starting_locations.write_file(os.path.join(model_ws,srt_loc),dis,start_time,27)

sim = flopy.modpath.mpsim.ModpathSim(model=mp, option_flags=[2,1,2,1,2,2,2,3,1,1,1,1], time_ct = 3, time_pts = [2500, 5000, 7500], strt_file='starting_locs.loc')
mp.write_input() # write files

mp.run_model(silent=False) # run model

# import digitized data csv
digitized = pd.read_csv(os.path.join('preproccessing','figure_7_distances.csv'))


# import modpath results
with open(os.path.join(model_ws,'test_case_1.mppth'), 'r') as f:
    lines_after_header = f.readlines()[3:]
    step = []
    step2 = []
    step3 = []
    step4 = []
    for line in lines_after_header:
        step4.append(line.split()[0])
        step.append(float(line.split()[4]))
        step2.append(float(line.split()[5]))
        step3.append(float(line.split()[6]))
df = pd.DataFrame({'ParticleID':step4,
                   'Time':step,
                   'GlobalX':step2,
                   'GlobalY':step3})


# equation for calculating the line length
def calc_line_length(globalx, globaly):
    line_length = np.sqrt((globalx**2)+(globaly**2))
    return line_length

# get the 0 day average from mppth
xlist0d = df.loc[(df['Time']==0.000000000000000E+00), ['ParticleID','Time','GlobalX','GlobalY']]

# get the 2500 day average from mppth
xlist25h = df.loc[(df['Time']==0.250000000000000E+04), ['ParticleID','Time','GlobalX','GlobalY']]
xlist25h['length']=np.sqrt((xlist25h['GlobalX']**2)+(xlist25h['GlobalY']**2))
av_len_25h = np.average(xlist25h['length'])

# get the 5000 day average from mppth
xlist5k = df.loc[(df['Time']==0.500000000000000E+04), ['ParticleID','Time','GlobalX','GlobalY']]
xlist5k['length']=np.sqrt((xlist5k['GlobalX']**2)+(xlist5k['GlobalY']**2))
av_len_5k = np.average(xlist5k['length'])

# get the 7500 day average from mppth
xlist75h = df.loc[(df['Time']==0.750000000000000E+04), ['ParticleID','Time','GlobalX','GlobalY']]
xlist75h['length']=np.sqrt((xlist75h['GlobalX']**2)+(xlist75h['GlobalY']**2))
av_len_75h = np.average(xlist75h['length'])

mppth_all = [av_len_25h, av_len_5k, av_len_75h]

# get the 2500 day average from digitized file
dig_xlist25h = digitized.loc[(digitized['days']==2500), ['distance']]
dig_av_len_25h = np.average(dig_xlist25h['distance'])

# get the 5000 day average from digitized file
dig_xlist5k = digitized.loc[(digitized['days']==5000), ['distance']]
dig_av_len_5k = np.average(dig_xlist5k['distance'])

# get the 7500 day average from digitized file
dig_xlist75h = digitized.loc[(digitized['days']==7500), ['distance']]
dig_av_len_75h = np.average(dig_xlist75h['distance'])

dig_all = [dig_av_len_25h, dig_av_len_5k, dig_av_len_75h]

# calculate percent difference
perd_tc1 = []
perdl=[perd_tc1.append(((dig_all[i] - mppth_all[i])/(dig_all[i]+mppth_all[i]/2))*100) for i in range(0,len(mppth_all))]

# determine pass/fail

pf_tc1 = []

for item in perd_tc1:
    if abs(item) > 5.:
        pf_tc1.append('Fail')
    else:
        pf_tc1.append('Pass')

# compile everything

dictionary = {'Time_Days':[2500, 5000, 7500], 'Digitized_dist_ft':dig_all, 'Current_run_ft':mppth_all, 'Percent_difference':perd_tc1, 'Pass/Fail':pf_tc1}
output=pd.DataFrame(dictionary)
# print(output)

outpath = os.path.join('output')
if not os.path.exists(outpath): os.mkdir(outpath)
figures = os.path.join('output','figures')
if not os.path.exists(figures): os.mkdir(figures)


out_csv = 'tc1_results.csv'
output.to_csv(os.path.join(outpath, out_csv),index=False)

# make figures
import flopy.utils.binaryfile as bf

headobj = bf.HeadFile(os.path.join(model_ws,'test_case_1.hds')) # make head object with hds file
times = [2500, 5000, 7500] # get the times
# print(times) # should be every 500 days

pthobj = flopy.utils.PathlineFile(os.path.join(model_ws,'test_case_1.mppth')) # create pathline object
epdobj = flopy.utils.EndpointFile(os.path.join(model_ws,'test_case_1.mpend')) # create endpoint object

fig_list = [] # initialize list of figure paths we will use to make a gif
for time in times:
    fig, ax = plt.subplots(figsize=(8,8))
    extent=(0,Lx,0,Ly)
    if time != 0:
        head = headobj.get_data(totim=times[-1])

    modelmap = flopy.plot.ModelMap(model=mf, layer=0, ax=ax)
    lc = modelmap.plot_grid(color='c',alpha=.25)
    qm = modelmap.plot_bc('CHD', alpha=0.5)

    well_epd = epdobj.get_alldata()
    well_pathlines = pthobj.get_alldata()
    modelmap.plot_pathline(well_pathlines, travel_time=f'<={time}', layer='all', color='red') # plot pathline <= time
    modelmap.plot_endpoint(well_epd, direction='starting', colorbar=False) # can only plot starting of ending, not as dynamic as pathlines
    fig_name = os.path.join(figures,f'{int(time)}_days.png') # figure path to save to
    fig.text(0.15, 0.85,
             f'Day = {int(time)}',
             fontsize=16, color='k',
             ha='left', va='bottom', alpha=1)
    plt.title('Pollock 1988 Ex. 1')
    # ax.set_ylim([0,delc*2])
    # ax.set_xlim([0,delc*2])
    fig.tight_layout()
    fig.savefig(fig_name)
plt.close('all') 