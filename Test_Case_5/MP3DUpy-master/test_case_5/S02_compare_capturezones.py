import os
import geopandas as gpd
import pandas as pd



mp3du_shp = gpd.read_file(os.path.join('output','mp3du_10_yrs_poly.shp'))
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

data = {'Case' : ['GWpath','Modpath6'],'Area_sqft':[gwpath_area, mp3du_area],'Area_acre':[gwpath_area*2.2957e-5, mp3du_area*2.2957e-5],'Left_extent':[gw_minx,mp3du_minx],'Lower_extent':[gw_miny,mp3du_miny],'Right_extent':[gw_maxx,mp3du_maxx],'Upper_extent':[gw_maxy,mp3du_maxy]}
df = pd.DataFrame(data)

df.to_csv(os.path.join('output','mp3du_well_capture_stats.csv'),index=False)





