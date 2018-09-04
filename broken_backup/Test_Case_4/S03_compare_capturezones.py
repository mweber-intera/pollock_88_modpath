import os
import geopandas as gpd
import pandas as pd



mp6_shp = gpd.read_file(os.path.join('output','shapefiles','mp6_10_yrs_poly.shp'))
mp6_area = mp6_shp.iloc[0].geometry.area

for row in pd.DataFrame(mp6_shp.bounds).iterrows():
	index, data = row
	minx6, miny6, maxx6, maxy6 = data
 


gwpath_shp = gpd.read_file(os.path.join('gwpath_digitized','fig_21_10_yr_capture_zone.shp'))
gwpath_shp.geometry = gwpath_shp.geometry.to_crs(mp6_shp.crs)

gwpath_area = gwpath_shp.iloc[0].geometry.area
for row in pd.DataFrame(gwpath_shp.bounds).iterrows():
	index, data = row
	gw_minx, gw_miny, gw_maxx, gw_maxy = data

columns = ['Case','Area_sqft','Area_acre','Left_extent','Lower_extent','Right_extent','Upper_extent']

def perc_diff(v1,v2):
	return abs((v2-v1)/(v2+v1))
area_pd = perc_diff(mp6_area,gwpath_area)

pf = 'Fail'
if area_pd <= 10.:
	pf = 'Pass'

data = {'Name' : ['GWpath','Modpath6','Percent Difference','Pass/Fail'],'Area_sqft':[gwpath_area, mp6_area, area_pd, pf],'Area_acre':[gwpath_area*2.2957e-5, mp6_area*2.2957e-5,area_pd,pf],'Left_extent':[gw_minx,minx6,'',''],'Lower_extent':[gw_miny,miny6,'',''],'Right_extent':[gw_maxx,maxx6,'',''],'Upper_extent':[gw_maxy,maxy6,'','']}
df = pd.DataFrame(data)

df.to_csv(os.path.join('output','tc4_results.csv'),index=False)





