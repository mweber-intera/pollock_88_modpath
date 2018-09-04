# create a modflow model and store it in \workspace
python S01_pre_process.py

# run modflow model in flopy
python S02_tc4.py


# create stats table comparing  10 year capture zones
python S03_post_process.py