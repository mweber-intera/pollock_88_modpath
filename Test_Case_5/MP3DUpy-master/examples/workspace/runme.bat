rem Run WRITEP3DGSF.EXE to write GSF file from DELR and DELC for structured grid
writep3dgsf.exe test_3_gsf.json colorcode
rem Run mod-path3du
mp3du.exe example_test_3.json colorcode
rem Write pathline shapefile
writep3doutput.exe out.json colorcode
	