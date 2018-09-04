# create a modflow model and store it in \workspace
python S01_make_model_grid.py

# run modflow model in flopy
python S02_flopy_make.py


# create stats table comparing  10 year capture zones
python S03_compare_capturezones.py