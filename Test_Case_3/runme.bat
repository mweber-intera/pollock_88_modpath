rem runme.bat will produce results for test case 3, this case compares an analytical well capture zone solution described by Grubb in 1993 to the results from a backwards particle track in modpath6
python S01_50_ft.py

python S02_50_ft_mp.py

rem produce stats tables
python S03_ymax_and_stagnation_point_50.py 