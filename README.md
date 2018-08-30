# README #

Python scripts for building and testing modflow and modpath models to test particle tracking for homogenous and heterogeneous examples as well as well capture zone analysis. 

## Installation notes

These tests were compiled with python using the following packages and versions:
=======
- Python = 3.6.5
- pandas = 0.23.3
- geopandas = 0.4.0
- matplotlib = 2.2.2
- flopy = 3.2.9 
- numpy = 1.14.2

If you do not yet have these packages installed, we recommend using the [conda](http://conda.pydata.org/docs/intro.html) package manager to install all the requirements 

Please note that Anaconda and Miniconda are python package distributors, this means that Anaconda will be downloaded to your machine and will contain a working version of python. 

(you can install [miniconda](http://conda.pydata.org/miniconda.html) or install the (larger) Anaconda
distribution, found at https://www.anaconda.com/download/).

Once this is installed, the following command will install all required packages in your Python environment, you may run this command out of a terminal if you add conda to your system's path, or you can simply use the Anaconda prompt:
(this may take a bit)
```
conda env create -f environment.yml
```
This will create a new environment called "modpath_qa"

To activate your new environment:
```
source activate modpath_qa
```

# Test Cases #
There are 5 test cases presented in this directory, each is to compare the USGS's modpath version 6 with alternative particle tracking solutions.

## Test Case 1
Test case 1 utilizes flopy and modpath6 to reproduce figure 7 in Pollock 1988

![alt text](https://github.com/rosskush/pollock_88_modpath/blob/master/Test_Case_1/fig7.PNG)

Particles are placed radially around the well cell in the bottom left corner and are tracked for 7,500 days.

![alt text](https://github.com/rosskush/pollock_88_modpath/blob/master//Test_Case_1/output/figures/7500_days.png)

To run this example follow these steps in a terminal or Anaconda prompt after moving to this directory:

(if not active already, activate the modpath_qa conda environment):
```
source activate modpath_qa
cd Test_Case_1
./runme.bat
```
This will produce a directory called output that plot figures and pass/fail statistics will be placed.

## Test Case 2
Test case 2 utilizes flopy and modpath6 to reproduce figure 10 in Pollock 1988

![alt text](https://github.com/rosskush/pollock_88_modpath/blob/master/Test_Case_2/fig10.png)

Particles are placed radially around the well cell in the bottom left corner and are tracked for 7,500 days.

![alt text](https://github.com/rosskush/pollock_88_modpath/blob/master//Test_Case_2/output/Compared_pathlines.png)

To run this example follow these steps in terminal or Anaconda prompt after moving to this directory:

(if not active already, activate the modpath_qa conda environment):
```
source activate modpath_qa
cd Test_Case_2
./runme.bat
```
This will produce a directory called output that plot figures and pass/fail statistics will be placed.


## Test Case 3
Test Case 3 compares an analytical well capture zone solution described by Grubb in 1993 to the results from a backward particle track in modpath6, this example assumes a homogeneous unconfined system with a single extraction well.

![alt text](https://github.com/rosskush/pollock_88_modpath/blob/master//Test_Case_3/output/backwards.png)


To run this example follow these steps in a terminal or Anaconda prompt after moving to this directory:

(if not active already, activate the modpath_qa conda environment):
```
source activate modpath_qa
cd Test_Case_3
./runme.bat
```
This will produce a directory called output that figures and pass/fail statistics will be placed.

## Test Case 4
Test Case 4 compares the 10 year well capture zone for a steady state aquifer with a heterogeneous hydraulic conductivity from an example from GWPATH (Shafer, 1987)

![alt text](https://github.com/rosskush/pollock_88_modpath/blob/master//Test_Case_4/preproccessing/hk_fig20.png)

![alt text](https://github.com/rosskush/pollock_88_modpath/blob/master//Test_Case_4/preproccessing/10_yr_capture_zone_fig21.png)

A modflow model was created to replicate this example and track backward particles with modpath 6

![alt text](https://github.com/rosskush/pollock_88_modpath/blob/master//Test_Case_4/outputs/pathline.png)

To run this example follow these steps in a terminal or Anaconda prompt after moving to this directory:

(if not active already, activate the modpath_qa conda environment):
```
source activate modpath_qa
cd Test_Case_4
./runme.bat
```
This will produce a directory called outputs that figures, shapefiles and pass/fail statistics will be placed.
(shapefiles include a grid of the model, the head contour after 10 years, and a bounding polygon of the 10-year capture zone)

## Test Case 5
Test Case 5 uses the same example from GWPATH (Shafer, 1987)

Although the modflow model is the same as Test Case 4, the backward particle tracking method used is SSPA's mod-PATH3DU version 2 (SSPA, 2018) 

![alt text](https://github.com/rosskush/pollock_88_modpath/blob/master//Test_Case_5/output/mp3du_pathline.png)

To run this example follow these steps in a terminal or Anaconda prompt after moving to this directory:

(if not active already, activate the modpath_qa conda environment):
```
source activate modpath_qa
cd Test_Case_5
./runme.bat
```
This will produce a directory called output that figures, shapefiles and pass/fail statistics will be placed.
(shapefiles include a bounding polygon of the 10-year capture zone, pathlines, and endpoints after 10 years)


# References #


sspa - mp3du version 2 http://mp3du.sspa.com/man/

pollock 1988

grubb 1993

Shafer 1987  

