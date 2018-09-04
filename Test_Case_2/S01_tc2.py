import flopy
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, Point


modelname = 'test_case_2'
exe = os.path.join('gw_codes','mf2k-chprc08spl.exe')
model_ws = os.path.join('workspace')
mf = flopy.modflow.Modflow(modelname, version='mf2k', exe_name =exe,model_ws=model_ws)

# DIS
proj4 = '+proj=aea +lat_1=27.5 +lat_2=35 +lat_0=31.25 +lon_0=-100 +x_0=1500000 +y_0=6000000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=us-ft +no_defs'
xul, yul = 5661342.80316535942256451, 19628009.74438977241516113
yll = yul-55

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


dis = flopy.modflow.ModflowDis(mf, nlay, nrow, ncol, delr=delr, delc=delc, top=top, botm=botm,nper=nper,perlen=perlen,xul=xul,yul=yul,proj4_str=proj4,lenuni=1)

mf.sr = flopy.utils.reference.SpatialReference(delr=dis.delr.array,delc=dis.delc.array,lenuni=1,xul=xul,yul=yul,proj4_str=proj4,prj=os.path.join('texas_gam.prj'))


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
chd = flopy.modflow.ModflowChd(mf, stress_period_data=lrcd)

#PCG
#I've seen examples of all three solvers being used
pcg = flopy.modflow.ModflowPcg(mf)

mf.write_input() # write modflow files
success, buff = mf.run_model(silent=False)



#modpath

mpexe = os.path.join("gw_codes","mp6.exe")

mp = flopy.modpath.Modpath('test_case_2',exe_name=mpexe,modflowmodel=mf,model_ws=model_ws,dis_file = mf.name+'.dis',head_file=mf.name+'.hds',budget_file=mf.name+'.cbc')

mp_ibound = mf.bas6.ibound.array # use ibound from modflow model
mpb = flopy.modpath.ModpathBas(mp,-1e30,ibound=mp_ibound,prsity=.3) # make modpath bas object

start_time=[0]

import Write_starting_locations
srt_loc = 'starting_locs_ex2.loc'
Write_starting_locations.write_file_ex2(os.path.join(model_ws,srt_loc),dis,start_time,10*4) # custom function in Write_starting_locations.py

sim = mp.create_mpsim(trackdir='forward', simtype='pathline', packages=srt_loc, start_time=(0, 0, 0)) # create simulation file

sim.time_ct = 10
time_pts =[]
for tp in range(sim.time_ct):
    time_pts.append(tp*2.18)

sim.time_pts = time_pts

mp.write_input() # write files

mp.run_model(silent=False) # run model

# Post-Processing: Percent difference calculation

# pull the x/y data from the shapefile
shp = (os.path.join('preproccessing',"digitize", 'endpoints.shp'))
df = gpd.read_file(shp)

lon = []
lat = []
lon = df.geometry.x
lat = df.geometry.y
pid=df.id

shp_pts = {'ParticleID':pid, 'PointX':lon, 'PointY':lat}

shppt = pd.DataFrame(shp_pts)

# Point name
with open(os.path.join('workspace','test_case_2.mpend'), 'r') as f:
    lines_after_header = f.readlines()[6:]
    stepp = []
    for line in lines_after_header:
        stepp.append(line.split()[0])
floatp = [float(x) for x in stepp]


# x data
with open(os.path.join('workspace','test_case_2.mpend'), 'r') as f:
    lines_after_header = f.readlines()[6:]
    stepx = []
    for line in lines_after_header:
        stepx.append(line.split()[26])
floatx = [float(x) for x in stepx]


# y data
with open(os.path.join('workspace','test_case_2.mpend'), 'r') as f:
    lines_after_header = f.readlines()[6:]
    stepy = []
    for line in lines_after_header:
        stepy.append(line.split()[27])
floaty = [float(x) for x in stepy]


# combine them into a dictionary
dictionary = {'ParticleID':floatp,'ParticleX':floatx,'ParticleY':floaty}

dict1 = pd.DataFrame(dictionary)

def per_diff(xpt,xmp):
    perd=(((xpt-xmp)/((xpt+xmp)/2))*100)
    return perd
def pass_fail(x):
    if abs(x)>10.:
        tc='fail'
        return tc
    else:
        tc='pass'
        return tc

results = dict1.merge(shppt,on='ParticleID')
results['localpX'] = results.PointX - xul
results['localpY'] = results.PointY - yll
results['PerdX'] = per_diff(xpt=results['localpX'], xmp=results['ParticleX'])
results['PerdY'] = per_diff(xpt=results['localpY'], xmp=results['ParticleY'])


# For plotting pathline
names = ['ParticleID', 'Particle_Group', 'Time_Point_Index', 'Cumulative_TimeStep', 'Tracking_Time', 'Global_X', 'Global_y', 'Global_Z', 'Layer', 'Row', 'Column', 'Grid', 'Local_X', 'Local_Y', 'Local_Z', 'Line_Segment_Index']
pathline_gdf = pd.read_csv(os.path.join(model_ws,'test_case_2.mppth'),skiprows=3,delim_whitespace=True, names=names)
pathline_gdf['geometry'] = pathline_gdf.apply(lambda xy: (xy['Global_X'],xy['Global_y']),axis=1)

pathline_gdf = pathline_gdf.groupby(['ParticleID'])['geometry'].apply(lambda x: LineString(x.tolist()))
pathline_gdf = gpd.GeoDataFrame(pathline_gdf,geometry='geometry',crs='texas_gam.prj')

def coords_to_mf_cords(xll,yll,ls):
    new_points = []
    for point in ls.coords:
        new_points.append((point[0]-xul,point[1]-yll))  
    return LineString(new_points)

xll, yll = mf.sr.xll, mf.sr.yll

fig, ax = plt.subplots(figsize=(8,6))

mf.sr.xul = 0 # just for plotting
mf.sr.yul = 55
modelmap = flopy.plot.ModelMap(model=mf, layer=0, ax=ax)
lc = modelmap.plot_grid(color='c',alpha=.25)
qm = modelmap.plot_bc('CHD', alpha=0.5)
ib = modelmap.plot_ibound()


shp = os.path.join('preproccessing',"digitize", 'figure_10_flownet.shp')
dfs = gpd.read_file(shp)
dfs.geometry = dfs.apply(lambda xy: coords_to_mf_cords(xll,yll,xy['geometry']),axis=1)

dfs.plot(ax=ax,color='k',label='Digitized Pathlines')
pathline_gdf.plot(ax=ax,color='r',label='Modpath6 Pathlines')

plt.title('Digitized and Modeled Pathlines')

ax.legend()
fig.tight_layout()

fig.savefig(os.path.join('output','Compared_pathlines.png'))

listx =[]

for index, row in results.iterrows():
    value=pass_fail(results.loc[index,'PerdX'])
    listx.append(value)

listy =[]

for index, row in results.iterrows():
    value=pass_fail(results.loc[index,'PerdY'])
    listy.append(value)


results['PassFailX'] = listx
results['PassFailY'] = listy


out_csv = 'tc2_results.csv'
results.to_csv(os.path.join('output',out_csv), index=False)


# Post-Processing: Figures

# Map the digitized shapefile against the modpath outputs

# read the line shapefile and pull the point data


import flopy.utils.binaryfile as bf

headobj = bf.HeadFile(os.path.join(model_ws,'test_case_2.hds')) # make head object with hds file
times = [0] + headobj.get_times() # get the times

pthobj = flopy.utils.PathlineFile(os.path.join(model_ws,'test_case_2.mppth')) # create pathline object
epdobj = flopy.utils.EndpointFile(os.path.join(model_ws,'test_case_2.mpend')) # create endpoint object

figures = os.path.join('output','figures')
if not os.path.exists(figures): os.mkdir(figures)