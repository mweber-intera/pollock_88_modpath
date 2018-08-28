rem runme.bat will produce results for test case 3, this case compares an analytical well capture zone solution described by Grubb in 1993 to the results from a backwards particle track in modpath6
python 50_ft.py

python 50_ft_mp.py

rem produce stats tables
python ymax_and_stagnation_point_50.py 