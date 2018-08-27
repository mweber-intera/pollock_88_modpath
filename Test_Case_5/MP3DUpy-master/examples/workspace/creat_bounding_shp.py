import geopandas as gpd
from shapely.geometry import Point, MultiPoint, LineString, Polygon,MultiPolygon
import pandas as pd
import os

gdf = gpd.read_file('endpoint.shp')


gdf['geometry'] = gdf['geometry'].apply(lambda x:x.coords[0])
gdf['end'] = 'final'
crs = gdf.crs


df = pd.DataFrame(gdf)



df = df.groupby(['end'])['geometry'].apply(lambda x: Polygon(x.tolist()))
gdf = gpd.GeoDataFrame(df,geometry='geometry')
gdf.crs = crs
gdf.to_file(os.path.join('ending_poly.shp'))
print(gdf['geometry'].area)

