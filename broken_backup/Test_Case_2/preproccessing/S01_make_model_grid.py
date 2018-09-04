import flopy
import os
import shutil


proj4 = '+proj=aea +lat_1=27.5 +lat_2=35 +lat_0=31.25 +lon_0=-100 +x_0=1500000 +y_0=6000000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=us-ft +no_defs'


xul, yul = 5661342.80316535942256451, 19628009.74438977241516113


mf = flopy.modflow.Modflow('grid')


Lx, Ly = 105, 55

nrow, ncol = 11, 21
delr, delc = int(Lx/ncol), int(Ly/nrow)



dis = flopy.modflow.ModflowDis(mf,1,nrow,ncol,lenuni=1,delr=delr,delc=delc,xul=xul, yul=yul,proj4_str=proj4)
# mf.sr = flopy.utils.reference.SpatialReference(prj=os.path.join('gwpath_rasters','starting_location.prj'),delr=delr,delc=delc,yul=yul)
dis.export(os.path.join('..','output','shapefiles',f'grid.shp'),prj=os.path.join('..','texas_gam.prj'))

# shutil.copy(os.path.join('gwpath_rasters','starting_location.prj'),os.path.join('output','shapefiles',f'grid.prj'))
