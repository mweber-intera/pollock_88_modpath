import flopy
import os
import numpy as np
import matplotlib.pyplot as plt
import platform
import imageio
import pandas as pd # pandas is a package that is used to work with dataframes (stolen from the R language) this will be
# how we import csv files


model_ws = os.path.join('pollock_model_ex1')
if not os.path.exists(model_ws): os.mkdir(model_ws)
gw_codes = os.path.join('gw_codes')
exe = os.path.join(gw_codes,'mfnwt.exe')
if platform.system() == 'Darwin':
    exe = 'mfnwt' # assuming you have mfnwt in your path
mf = flopy.modflow.Modflow('pollock_88',version='mfnwt',exe_name=exe,model_ws=model_ws)



nlay = 1 # number of layers
nrow, ncol = 40,40 # number of rows and columns
top = np.ones((nrow,ncol)) * 100 # 2d array of size (nrow * ncol) * 100
botm = np.ones((nlay,nrow,ncol)) * 0 # 2d array of size (nrow * ncol) * 0
delr, delc = 100, 100 # hieght and width of each cell
Lx, Ly = delr*ncol, delc*nrow # model width and hieght in ft


nper = 15 # number of stress periods
perlen = [500] # number time unites in first stress period (this case 500 days)
steady = [True] # steady state or transient in first stress period
nstp = [1] # number of time steps in first stress period
for sp in range(0,nper-1):
    perlen.append(500) # number time unites in each stress period
    steady.append(True) # steady state or transient in each stress period
    nstp.append(1) # number of time steps in each stress period
laycbd = 0


dis = flopy.modflow.ModflowDis(mf,nlay,nrow,ncol,nper,delr,delc,0,top,botm,perlen,nstp,1,steady) # create dis object

upw = flopy.modflow.ModflowUpw(mf,hk=10,ipakcb=53) # creat upw object 

ibound = np.zeros((nlay,nrow,ncol))
ibound[0][:int(nrow/2),int(ncol/2):] = 1
bas = flopy.modflow.ModflowBas(mf, ibound=1, strt=100.0) # create bas object, all cells are active, starting head = 100 ft

spd = {} # initialize spd for oc
for i in range(dis.nper):
    spd[(i, 0)] = ['save head', 'save budget']
oc = flopy.modflow.ModflowOc(mf, stress_period_data=spd, compact=True) # compact = True to use in modpath later

nwt = flopy.modflow.ModflowNwt(mf, maxiterout=5000, linmeth=2, iprnwt=1) # solver for modflow nwt

Qcfd = 160000./4 # Q cf-days
wel_spd = {} 
for sp in range(nper):
    wel_spd[sp] = [0,nrow-1,0,Qcfd] # injection well is in center of the model


print(wel_spd) # {nper:[layer, row, column, Q],nper+1:[layer, row, column, Q],....} # make sure to use python indexing 
wel = flopy.modflow.ModflowWel(mf,stress_period_data=wel_spd) # well package

''' # commented this out to instead use the csv Mary created for placing the chds
# this is the math used to make a circle with radius 4000 ft (40 cells)
# the permiter of the cirlce will be constant head boundries that have a head = 100 ft 

def createCircularMask(h, w, center=None, radius=None):
    # creates a binary mask of the 2d array, True means the value is the circular paremter. 
    if center is None: # use the middle of the image
        center = [int(w/2), int(h/2)]
    if radius is None: # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    mask = (dist_from_center < radius+1) & (dist_from_center >= radius)
    return mask

mask = createCircularMask(ncol,nrow,radius=40)
chd_locsX, chd_locsY = np.where(mask)[0], np.where(mask)[1] # get the x and y locations for the binary mask


chd_dat = [] # initialize spress period data for constant head boundry 
for i in range(len(chd_locsX)):
    cx,cy = chd_locsX[i], chd_locsY[i]
    try:
        if ibound[0][cx,cy] == 1: # if ibound is active, then append to chd data
            chd_dat.append([0,cx,cy,100,100]) # [layer, row, col, start_head, end head]
    except:
        pass
'''

chd_df = pd.read_csv('chb_t1.csv') # read in csv with pandas
print(chd_df.head()) # printing with .head() lets you see the first 5 rows of a dataframe

chd_dat = []
for i, vals in chd_df.iterrows(): # fancy for loop that returns the index in i, and the values in vals
    row, col = vals # unpack row and col
    col = col  # shift col to the right 40 cells
    chd_dat.append([0,int(row),int(col),100,100])



chd_spd = {0:chd_dat} # only need do do in the first stress period since modflow uses the previous stress period if there is nothing in the current stress period.
print(chd_spd)
chd = flopy.modflow.ModflowChd(mf,stress_period_data=chd_spd)




mf.write_input() # write modflow files
# mf.run_model() # run model




# now for modpath

mpexe = os.path.join(gw_codes,'mp6.exe')
if platform.system() == 'Darwin':
    mpexe = 'mp6' # assuming you have mp6 in your path

mp = flopy.modpath.Modpath('pollock_88_mp',exe_name=mpexe,modflowmodel=mf,model_ws=model_ws,dis_file = mf.name+'.dis',head_file=mf.name+'.hds',budget_file=mf.name+'.cbc')

mp_ibound = mf.bas6.ibound.array # use ibound from modflow model 
mpb = flopy.modpath.ModpathBas(mp,upw.hdry,ibound=mp_ibound,prsity=.3) # make modpath bas object

start_time=[0]

import Write_starting_locations # this is a script I made that write the starting location file, it is not a straight forward and is unique to this model but can be modified to create a different starting locations file.
srt_loc = 'starting_locs.loc' # name starting locations file
Write_starting_locations.write_file(os.path.join(model_ws,srt_loc),dis,start_time,10*4) # custom function in Write_starting_locations.py

sim = mp.create_mpsim(trackdir='forward', simtype='pathline', packages=srt_loc, start_time=(0, 0, 0)) # create simulation file
mp.write_input() # write files

mp.run_model(silent=False) # run model



# post proccesing

import flopy.utils.binaryfile as bf

headobj = bf.HeadFile(os.path.join(model_ws,'pollock_88.hds')) # make head object with hds file
times = [0] + headobj.get_times() # get the times (we made this in the begining with the dis)
print(times) # should be every 500 days, but I added "0" to the begging so we can see when there is no pumping

pthobj = flopy.utils.PathlineFile(os.path.join(model_ws,'pollock_88_mp.mppth')) # create pathline object
epdobj = flopy.utils.EndpointFile(os.path.join(model_ws,'pollock_88_mp.mpend')) # create endpoint object

fig_list = [] # initialize list of figure paths we will use to make a gif
for time in times:
    fig, ax = plt.subplots(figsize=(8,8))
    extent=(0,Lx,0,Ly)
    if time != 0:
        head = headobj.get_data(totim=times[-1])
        CS = plt.contour(np.flipud(head[0]), extent=extent, color='k')
        plt.clabel(CS, inline=1, fontsize=10)
        # plt.imshow(head[0],cmap='cubehelix',extent=extent)
        # plt.colorbar()

    modelmap = flopy.plot.ModelMap(model=mf, layer=0, ax=ax)
    lc = modelmap.plot_grid(color='c',alpha=.25)
    qm = modelmap.plot_bc('CHD', alpha=0.5)

    well_epd = epdobj.get_alldata()
    well_pathlines = pthobj.get_alldata()
    modelmap.plot_pathline(well_pathlines, travel_time=f'<={time}', layer='all', colors='red') # plot pathline <= time
    modelmap.plot_endpoint(well_epd, direction='starting', colorbar=False) # can only plot starting of ending, not as dynamic as pathlines
    fig_name = os.path.join('figures',f'{int(time)}_days.png') # figure path to save to
    fig.text(0.15, 0.85,
             f'Day = {int(time)}',
             fontsize=16, color='k',
             ha='left', va='bottom', alpha=1)
    plt.title('Pollock 1988 Ex. 1')
    # ax.set_ylim([0,delc*2])
    # ax.set_xlim([0,delc*2])
    fig.tight_layout()
    fig.savefig(fig_name)
    fig_list.append(imageio.imread(fig_name)) # append imagio.imread() for each figure path
    plt.close()


imageio.mimsave(os.path.join('figures','final_gif.gif'),fig_list,duration=.25) # now save a gif of all the figures in fig_list

