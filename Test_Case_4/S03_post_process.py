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

offset = 160/2
xul, yul = 5661342.80316535942256451 - offset, 19628009.74438977241516113 + offset
yll = yul - 8000.
gw_minx_rel = gw_minx-xul
gw_maxx_rel = gw_maxx-xul
gw_miny_rel = gw_miny - yll
gw_maxy_rel = gw_maxy - yll

def perc_diff(v1,v2):
	return abs((v2-v1)/(v2+v1))*100
area_pd = perc_diff(mp6_area,gwpath_area)
lext_pd = perc_diff(minx6,gw_minx_rel)
rext_pd = perc_diff(maxx6,gw_maxx_rel)
uext_pd = perc_diff(maxy6,gw_maxy_rel)
lwext_pd = perc_diff(miny6,gw_miny_rel)

pf = 'Fail'
if area_pd <= 10.:
	pf = 'Pass'

pfl = 'Fail'
if lext_pd <= 10.:
	pfl = 'Pass'

pfr = 'Fail'
if rext_pd <= 10.:
	pfr = 'Pass'

pfu = 'Fail'
if uext_pd <= 10.:
	pfu = 'Pass'

pflw = 'Fail'
if lwext_pd <= 10.:
	pflw = 'Pass'

data = {'Name' : ['GWpath','Modpath6','Percent Difference','Pass/Fail'],'Area_sqft':[gwpath_area, mp6_area, area_pd, pf],
        'Area_acre':[gwpath_area*2.2957e-5, mp6_area*2.2957e-5,area_pd,pf],'Left_extent':[gw_minx_rel,minx6,lext_pd, pfl],
        'Lower_extent':[gw_miny_rel,miny6,lwext_pd, pflw],'Right_extent':[gw_maxx_rel,maxx6,rext_pd, pfr],
        'Upper_extent':[gw_maxy_rel,maxy6,uext_pd, pfu]}
df = pd.DataFrame(data)

df.to_csv(os.path.join('output','tc4_results.csv'),index=False)





