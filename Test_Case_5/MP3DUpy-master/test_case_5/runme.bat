
if not exist "output" mkdir output

rem Run WRITEP3DGSF.EXE to write GSF file from DELR and DELC for structured grid
..\gw_codes\writep3dgsf.exe gsf.json colorcode
rem Run mod-path3du with the primary file
..\gw_codes\mp3du.exe primary.json colorcode
rem export data from bin and write pathline shapefile 
..\gw_codes\writep3doutput.exe out.json colorcode

rem write shapefile and compare to GWpath
python S01_create_bounding_shp.py

python S02_compare_capturezones.py

