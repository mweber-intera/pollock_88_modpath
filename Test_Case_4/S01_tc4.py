import flopy
import numpy as np
import matplotlib.pyplot as plt
import flopy.utils.binaryfile as bf
import os
import geopandas as gpd

import pandas as pd
import geopandas
from shapely.geometry import Point
from flopy.utils.reference import SpatialReference


modelname = 'test_case_4'
exe = "../gw_codes/mf2k-chprc08spl.exe"
model_ws = os.path.join('workspace')
if not os.path.exists(model_ws): os.mkdir(model_ws)

output = os.path.join('output')
if not os.path.exists(output): os.mkdir(output)

shapefiles = os.path.join('output','shapefiles')
if not os.path.exists(shapefiles): os.mkdir(shapefiles)

griddata = 'preproccessing'

mf = flopy.modflow.Modflow(modelname, version='mf2k', exe_name =exe,model_ws=model_ws)

offset = 160/2
proj4 = '+proj=aea +lat_1=27.5 +lat_2=35 +lat_0=31.25 +lon_0=-100 +x_0=1500000 +y_0=6000000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=us-ft +no_defs'
xul, yul = 5661342.80316535942256451 - offset, 19628009.74438977241516113 + offset

#DIS
Lx = 8000. + 160
Ly = 8000. + 160
ztop = 150.
zbot = 0
nlay = 1

nrow,ncol = 51,51

delr, delc = int(Lx/ncol), int(Ly/nrow)
delv = (ztop - zbot) / nlay
botm = np.linspace(ztop, zbot, nlay + 1)
nper = 10 # annual for 10 years, find a way to do a steady-state period and then pipe in the values
perlen = 365.25

dis = flopy.modflow.ModflowDis(mf, nlay, nrow, ncol, delr=delr, delc=delc, top=ztop, botm=botm[1:],nper=nper,perlen=perlen,xul=xul,yul=yul,proj4_str=proj4,lenuni=1)

mf.sr = flopy.utils.reference.SpatialReference(delr=dis.delr.array,delc=dis.delc.array,lenuni=1,xul=xul,yul=yul,proj4_str=proj4,prj=os.path.join('texas_gam.prj'))

#BAS

# linear stepdown for starting heads and constant head boundries 
south_to_north = np.linspace(100,60,nrow)

ibound = np.ones((nlay, nrow, ncol), dtype=np.int32)
ibound[:, 0, :] = -1
ibound[:, -1, :] = -1
ibound[:, :, 0] = -1
ibound[:, :, -1] = -1

strt = np.ones((nlay, nrow, ncol), dtype=np.float32)*ztop
strt[:, :, :] = 100
strt[:, 0, :] = 100.
strt[:, -1, :] = 60.
for i in range(ncol-1):
    strt[:, :, i] = south_to_north
strt[:, :, 0] = south_to_north
strt[:, :, -1] = south_to_north

bas = flopy.modflow.ModflowBas(mf, ibound=ibound, strt=strt)


# use starting heads to create constant head boundries along the left and right columns
chd_spd = {}
spd = []
for row in range(nrow):
    stage = strt[0][row,0]
    spd.append([0,row,0,stage,stage])
    spd.append([0,row,ncol-1,stage,stage])
for col in range(ncol):
    stage=strt[0][0,col]
    spd.append([0, 0, col, 100, 100])
    spd.append([0,nrow-1,col,60,60])

chd_spd[0] = spd
chd = flopy.modflow.ModflowChd(mf,stress_period_data=chd_spd,ipakcb=53)

#LPF change hydraulic conductivity here

#gdf = gpd.read_file(os.path.join(griddata,f'grid_offset_{nrow}.shp'))
gdf = gpd.read_file(griddata+f'/grid_offset_{nrow}.shp')

hk_array = np.ones((nlay, nrow, ncol), dtype=np.int32)
for i in range(len(gdf)):
    r = gdf.iloc[i]['row']
    c = gdf.iloc[i]['column']
    val = gdf.iloc[i]['Hk']
    hk_array[0][r-1, c-1] = val
hk_array[0][:,0] = hk_array[0][:,1]
hk_array[0][0,:] = hk_array[0][1,:]

# print(hk_array)
lpf = flopy.modflow.ModflowLpf(mf, hk=hk_array, vka=hk_array, ipakcb=53)
lpf.hk.plot()
#OC
spd = {}
for sp in range(nper):
    spd[(sp, 0)] = ['print head', 'print budget', 'save head', 'save budget']
oc = flopy.modflow.ModflowOc(mf, stress_period_data=spd, compact=True)

pcg = flopy.modflow.ModflowPcg(mf)


# WEL
# well 1: 2400, 1600, 200 gpm
# well 2: 6400, 2880, 400 gpm
# well 3: 3840, 4640, 500 gpm
# well 4: 2880, 6720, 300 gpm
# 1 gpm = 192.5 ft**3 per day

gpm2cfd = 192.5


wel1 = [0, 9+1, 14+1, -200*gpm2cfd]
wel2 = [0, 17+1, 39+1,  -400*gpm2cfd]
wel3 = [0, 28+1, 23+1,  -500*gpm2cfd]
wel4 = [0, 41+1, 17+1,  -300*gpm2cfd]

wells = [wel1,wel2,wel3,wel4]

wel_spd = {0: wells, 1: wells, 2: wells, 3: wells, 4: wells, 5: wells, 6: wells, 7: wells,
           8: wells, 9: wells}
wel = flopy.modflow.ModflowWel(mf,stress_period_data=wel_spd,ipakcb=53)

#write the modflow input files
mf.write_input()

# Run the MODFLOW model
success, buff = mf.run_model(silent=False)

cbbobj = bf.CellBudgetFile(os.path.join(model_ws,modelname+'.cbc'))
# print(cbbobj.get_)

# create contour shapefile
headobj = bf.HeadFile(os.path.join(model_ws,modelname+'.hds'))
times = headobj.get_times()
head = headobj.get_data(totim=times[-1])

levels = np.arange(45,100,5)
extent = [xul,xul+Lx,yul-Ly,yul]

fig, ax = plt.subplots(figsize=(8,8))
plt.imshow(head[0],extent=extent,cmap='jet')
plt.colorbar()
plt.title('Head after 10 years (ft)'.title())
contour = plt.contour(np.flipud(head[0]),levels,extent=extent)

plt.clabel(contour, inline=1, fontsize=10,fmt='%1.0f',colors='k')



fig.tight_layout()
fig.savefig(os.path.join(output,'contour_head.png'))



head_shp = os.path.join(shapefiles,'head_contour.shp')
mf.sr.export_contours(head_shp,contour,prj=os.path.join('texas_gam.prj'),xul=xul,yul=yul)

plt.close('all')


model_ws = os.path.join('workspace')
modelname = 'test_case_4'
#mf = flopy.modflow.Modflow.load(modelname+'.nam',model_ws=model_ws)
# DIS
Lx = 8000. + 160.
Ly = 8000. + 160.
ztop = 150.
zbot = 0
nlay = 1
nrow, ncol = 51, 51
delr, delc = int(Lx / ncol), int(Ly / nrow)
delv = (ztop - zbot) / nlay
botm = np.linspace(ztop, zbot, nlay + 1)
nper = 10  # annual for 10 years, find a way to do a steady-state period and then pipe in the values
perlen = 365.2

# make a circle!
offset = 160 / 2
proj4 = '+proj=aea +lat_1=27.5 +lat_2=35 +lat_0=31.25 +lon_0=-100 +x_0=1500000 +y_0=6000000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=us-ft +no_defs'
xul, yul = 5661342.80316535942256451 - offset, 19628009.74438977241516113 + offset
# get the row/column!
delcl = np.ones(nrow) * (int(Lx / ncol))
delrl = delcl
sr = SpatialReference(delr=delrl, delc=delcl, xul=xul, yul=yul)
mf.sr = sr
yll = yul - 8000.  # measure from the bottom up
well3x = 3840. + offset
well3y = 8000. - 4640. - offset  # measure from the bottom up


def PointsInCircum(xul, yll, r, n=100):
    a = [[np.cos(2 * np.pi / n * i) * r, np.sin(2 * np.pi / n * i) * r] for i in range(0, n)]
    x0 = np.array([i[0] for i in a])
    y0 = np.array([i[1] for i in a])
    return [x0 + xul + well3x, y0 + yll + well3y]


test = PointsInCircum(xul, yll, 50, 100)
xcirc = test[0].tolist()
ycirc = test[1].tolist()

# make a shapefile!

circle = pd.DataFrame({'x': xcirc, 'y': ycirc})
# get model coordinates
circle['ModelX'] = circle['x'] - xul
circle['ModelY'] = yul - circle['y']
rows, cols = sr.get_rc(circle['x'].tolist(), circle['y'].tolist())
circle['Row'], circle['Column'] = rows, cols



# get the local coordinates for input to modpath6
def calc_local_x(delr, col, x):
    temp_x = delr * (col)
    val = x - temp_x
    localX = val / delr
    return localX

def calc_local_y(delc, row, y, nrow):
    temp_y = delc * (row)
    val = temp_y - y
    localY = 1+(val / delc)
    return localY


circle['LocalX'] = circle.apply(lambda xy: calc_local_x(delr, xy['Column'], xy['ModelX']), axis=1)
circle['LocalY'] = circle.apply(lambda xy: calc_local_y(delc, xy['Row'], xy['ModelY'],nrow), axis=1)



circle['cirque'] = circle.apply(lambda x: Point((float(x.x), float(x.y))), axis=1)
circle = geopandas.GeoDataFrame(circle, geometry='cirque')
proj4 = '+proj=aea +lat_1=27.5 +lat_2=35 +lat_0=31.25 +lon_0=-100 +x_0=1500000 +y_0=6000000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=us-ft +no_defs'
# circle.to_file(os.path.join('shapefiles', 'starting_circle.shp'), driver='ESRI Shapefile')
# shutil.copy(os.path.join('grid', 'grid.prj'), os.path.join('shapefiles', 'starting_circle.prj'))


# back to normal pandas
df = pd.DataFrame(circle)
df['ParticleID'] = np.arange(1,len(df)+1)
df['GroupNumber'] = 1
df['Grid'] = 1
df['Layer'] = 1
df['LocalZ'] = .5
df['ReleaseTime'] = 0
df['Label'] = 'GP01'
df['Row'] += 1 # for writing starting loc
df['Column'] += 1
df = df[['ParticleID', 'GroupNumber', 'Grid', 'Layer', 'Row', 'Column', 'LocalX', 'LocalY', 'LocalZ', 'ReleaseTime','Label', 'x', 'y']]
df.to_csv(os.path.join(model_ws,'starting_locs.csv'), index=False)

def write_loc_file(file_nam,starting_csv,strt_time=0,input_style=1):
    df = pd.read_csv(starting_csv)
    columns = ['ParticleID', 'GroupNumber', 'Grid', 'Layer', 'Row', 'Column', 'LocalX', 'LocalY', 'LocalZ',
             'ReleaseTime', 'Label']
    grps = df['GroupNumber'].unique().tolist()

    # print(grps)
    file = open(file_nam,'w')
    file.write(f'1\n{len(grps)}\n')
    for grp in grps:
        tempDF = df[df['GroupNumber'] == grp]
        grp_nam = tempDF.iloc[0]['Label']
        file.write(f'{grp_nam}'+'\n')
        file.write(f'{len(tempDF)}\n')
    for grp in grps:
        tempDF = df[df['GroupNumber'] == grp]
        grp_nam = tempDF.iloc[0]['Label']
        for z in range(len(tempDF)):
            for j in columns:
                file.write(f'{tempDF.iloc[z][j]}  ')
            file.write('\n')

starting_loc = os.path.join(model_ws,'starting_pts.loc')

write_loc_file(starting_loc,starting_csv=os.path.join(model_ws,'starting_locs.csv'))

mp6_exe = "../gw_codes/mp6.exe"

mp = flopy.modpath.Modpath('test_case_4',exe_name=mp6_exe,modflowmodel=mf,model_ws=model_ws,dis_file = mf.name+'.dis',head_file=mf.name+'.hds',budget_file=mf.name+'.cbc')
mp_ibound = mf.bas6.ibound.array # use ibound from modflow model
mpb = flopy.modpath.ModpathBas(mp,-1e30,ibound=mp_ibound,prsity =.25) # make modpath bas object

# run the simulation two times, first for pathline then for time series
sim = mp.create_mpsim(trackdir='backward', simtype='pathline', packages='starting_pts.loc',
                      start_time=(0, 0, 0))  # create simulation file

mp.write_input()
mp.run_model(silent=False)

# now create the sim file for timeseries backwards tracking
sim = flopy.modpath.ModpathSim(mp,mp.nam,mp.lst,option_flags=[3,2,2,1,2,2,2,3,1,1,1,1],stop_time=3652,strt_file='starting_pts.loc',time_pts=np.arange(365.2,3652.1,365.2),time_ct=10)

mp.write_input()
mp.run_model(silent=False)

cbb = bf.CellBudgetFile(os.path.join(model_ws,modelname+'.cbc'))


pthobj = flopy.utils.PathlineFile(os.path.join(model_ws,'test_case_4.mppth')) # create pathline object
# epdobj = flopy.utils.EndpointFile(os.path.join(model_ws,'test_case_4.mpend')) # create endpoint object

fig, ax = plt.subplots(figsize=(8,8))

hds = bf.HeadFile(os.path.join(model_ws,modelname+'.hds'))
times = hds.get_times()
head = hds.get_data(totim=times[-1])
levels = np.linspace(0, 10, 11)

frf = cbb.get_data(text='FLOW RIGHT FACE', totim=times[-1])[0]
fff = cbb.get_data(text='FLOW FRONT FACE', totim=times[-1])[0]
mf.sr.xul, mf.sr.yul = 0, 8000 + 160

modelmap = flopy.plot.ModelMap(model=mf, layer=0)
qm = modelmap.plot_ibound()
lc = modelmap.plot_grid()

quiver = modelmap.plot_discharge(frf, fff, head=head)

# well_epd = epdobj.get_alldata()
well_pathlines = pthobj.get_alldata()


modelmap.plot_pathline(well_pathlines, travel_time='<= 3652.5', layer='all', colors='red') # plot pathline <= time
# modelmap.plot_endpoint(well_epd, direction='ending', colorbar=False) # can only plot starting of ending, not as dynamic as pathlines
modelmap.plot_bc('wel',color='k')

outputs = os.path.join('output')
if not os.path.exists(outputs): os.mkdir(outputs)

plt.title('Pathline of particles after 10 years'.title())
fig.tight_layout()
fig.savefig(os.path.join(outputs,'pathline.png'))


plt.close('all')
import pandas as pd
import os
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, MultiPoint, LineString, Polygon,MultiPolygon
from flopy.utils.reference import SpatialReference
import flopy.utils.binaryfile as bf
import shutil
import flopy

pd.set_option("display.max_rows",8)

model_ws = os.path.join('workspace')
modelname = 'test_case_4'

names = ['Time Point Index','Cumulative Time Step','Tracking Time','Particle ID','Particle Group','Global X','Global Y','Global Z','Grid','Layer','Row','Column','Local X','Local Y','Local Z']
names = [item.replace(' ','_') for item in names]
ts = pd.read_csv(os.path.join(model_ws,modelname+'.mp.tim_ser'),skiprows=3,names=names,delim_whitespace=True)
ts = ts.loc[ts['Tracking_Time'] <= 3652]

#mf = flopy.modflow.Modflow.load(modelname+'.nam',model_ws=model_ws)

sr = mf.sr
Lx = np.sum(mf.dis.delr.array)
Ly = np.sum(mf.dis.delc.array)

def get_gamx(globalx,xul,Lx):
    gamx = xul - globalx + Lx
    dif = xul - gamx
    gamx = xul + Lx + dif
    return gamx

def get_gamy(globaly,yul,Ly):
    gamy = yul - globaly + Ly
    dif = yul - gamy
    gamy = yul + dif
    return gamy


ts['GAMX'] = sr.xul - ts['Global_X'] + Lx
ts['GAMY'] = sr.yul - ts['Global_Y']

ts['GAMX'] = ts.apply(lambda xy: get_gamx(xy['Global_X'],sr.xul,Lx),axis=1)
ts['GAMY'] = ts.apply(lambda xy: get_gamy(xy['Global_Y'],sr.yul,Ly),axis=1)


ts['geometry'] = ts.apply(lambda xy: Point(xy['GAMX'],xy['GAMY']),axis=1)

gdf = gpd.GeoDataFrame(ts,geometry='geometry')
gdf = gdf[gdf['Tracking_Time']>=3650] # get 10 years
points = gdf['geometry']
point_collection = MultiPoint(list(points))

# make a polygon using the points after 10 years
df2 = pd.DataFrame({'geometry':points,'end':'end_pt'})
df2['geometry'] = df2['geometry'].apply(lambda x:x.coords[0])
df2.reset_index(inplace=True,drop=True)
df2 = df2.groupby(['end'])['geometry'].apply(lambda x: Polygon(x.tolist()))
gdf2 = gpd.GeoDataFrame(df2,geometry='geometry')

output = os.path.join('output')
if not os.path.exists(output): os.mkdir(output)
shapefiles = os.path.join('output','shapefiles')
if not os.path.exists(shapefiles): os.mkdir(shapefiles)

gdf2.to_file(os.path.join(shapefiles,'mp6_10_yrs_poly.shp'))
shutil.copy(os.path.join('texas_gam.prj'),os.path.join(shapefiles,'mp6_10_yrs_poly.prj'))
