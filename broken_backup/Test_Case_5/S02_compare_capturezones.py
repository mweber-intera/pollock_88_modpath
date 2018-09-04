import os
import geopandas as gpd
import pandas as pd
import flopy
import numpy as np
from shapely.geometry import LineString


mp3du_shp = gpd.read_file(os.path.join('output','shapefiles','mp3du_10_yrs_poly.shp'))
mp3du_area = mp3du_shp.iloc[0].geometry.area

for row in pd.DataFrame(mp3du_shp.bounds).iterrows():
	index, data = row
	mp3du_minx, mp3du_miny, mp3du_maxx, mp3du_maxy = data
# 


gwpath_shp = gpd.read_file(os.path.join('gwpath_digitized','fig_21_10_yr_capture_zone.shp'))
gwpath_shp.geometry = gwpath_shp.geometry.to_crs(mp3du_shp.crs)

gwpath_area = gwpath_shp.iloc[0].geometry.area
for row in pd.DataFrame(gwpath_shp.bounds).iterrows():
	index, data = row
	gw_minx, gw_miny, gw_maxx, gw_maxy = data
# print(minx6, miny6, maxx6, maxy6)

columns = ['Case','Area_sqft','Area_acre','Left_extent','Lower_extent','Right_extent','Upper_extent']

def perc_diff(v1,v2):
	return abs((v2-v1)/(v2+v1))
area_pd = perc_diff(mp3du_area,gwpath_area)

pf = 'Fail'
if area_pd <= 10.:
	pf = 'Pass'

data = {'Name' : ['GWpath','Modpath6','Percent Difference','Pass/Fail'],'Area_sqft':[gwpath_area, mp3du_area, area_pd, pf],'Area_acre':[gwpath_area*2.2957e-5, mp3du_area*2.2957e-5,area_pd,pf],'Left_extent':[gw_minx,mp3du_minx,'',''],'Lower_extent':[gw_miny,mp3du_miny,'',''],'Right_extent':[gw_maxx,mp3du_maxx,'',''],'Upper_extent':[gw_maxy,mp3du_maxy,'','']}
df = pd.DataFrame(data)

df.to_csv(os.path.join('output','tc5_results.csv'),index=False)

def coords_to_mf_cords(xll,yll,ls):
	new_points = []
	for point in ls.coords:
		new_points.append((point[0]-xul,point[1]-yll))  
	return LineString(new_points)





import matplotlib.pyplot as plt
import flopy.utils.binaryfile as bf
model_ws = ''
modelname = 'test_case_5'
mf = flopy.modflow.Modflow.load(f'{modelname}.nam',check=False)
xul, yul = mf.sr.xul, mf.sr.yul
xll, yll = mf.sr.xll, mf.sr.yll

mf.sr.xul, mf.sr.yul = 0, 8000  + 160

mp3du_pathlines = gpd.read_file(os.path.join('output','shapefiles','Pathline_mp3du.shp'))
mp3du_pathlines.geometry = mp3du_pathlines.apply(lambda xy: coords_to_mf_cords(xll,yll,xy['geometry']),axis=1)


# exit()


fig, ax = plt.subplots(figsize=(8,8))

hds = bf.HeadFile(os.path.join(model_ws,modelname+'.hds'))
times = hds.get_times()
head = hds.get_data(totim=times[-1])

cbb = bf.CellBudgetFile(os.path.join(model_ws,modelname+'.cbc'))

frf = cbb.get_data(text='FLOW RIGHT FACE', totim=times[-1])[0]
fff = cbb.get_data(text='FLOW FRONT FACE', totim=times[-1])[0]

modelmap = flopy.plot.ModelMap(model=mf, layer=0)
qm = modelmap.plot_ibound()
lc = modelmap.plot_grid()

quiver = modelmap.plot_discharge(frf, fff, head=head)
modelmap.plot_bc('wel',color='k')
mp3du_pathlines.plot(ax=ax)


outputs = os.path.join('output')
if not os.path.exists(outputs): os.mkdir(outputs)

plt.title('Pathline of particles after 10 years'.title()+' (mp3du)')
fig.tight_layout()
fig.savefig(os.path.join(outputs,'mp3du_pathline.png'))



plt.close('all')



