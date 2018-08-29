import geopandas as gpd
from shapely.geometry import Point, MultiPoint, LineString, Polygon,MultiPolygon
import pandas as pd
import os
import shutil

shps = os.listdir(os.path.join('output','shapefiles'))
shps = [item for item in shps if item.endswith('.shp')]

for shp in shps:
	shutil.copy('texas_gam.prj',os.path.join('output','shapefiles',shp.replace('.shp','.prj')))


gdf = gpd.read_file(os.path.join('output','shapefiles','Endpoint_mp3du.shp'))


gdf['geometry'] = gdf['geometry'].apply(lambda x:x.coords[0])
gdf['end'] = 'final'
crs = gdf.crs


df = pd.DataFrame(gdf)

df = df.groupby(['end'])['geometry'].apply(lambda x: Polygon(x.tolist()))
gdf = gpd.GeoDataFrame(df,geometry='geometry')
gdf.crs = crs

if not os.path.exists(os.path.join('output','shapefiles')): os.mkdir(os.path.join('output','shapefiles'))

gdf.to_file(os.path.join('output','shapefiles','mp3du_10_yrs_poly.shp'))

