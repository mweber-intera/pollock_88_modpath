# README #

Python scripts for building modflow and modpath models to test particle tracking for homogenous and hetergenous examples as well as well capture zone analysis. 

## Installation notes

These tests were compiled with python using the following packages and versions:
=======
- Python = 3.6.5
- pandas = 0.23.3
- geopandas = 0.4.0
- matplotlib = 2.2.2
- flopy = 3.2.9 
- numpy = 1.14.2

If you do not yet have these packages installed, we recommend to use the [conda](http://conda.pydata.org/docs/intro.html) package manager to install all the requirements 

Please note that Anaconda and Miniconda are python package distibuters, this means that Anaconda will be downloaded to your machine and will conatiain a working version of python. 

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

=======

# Test Cases #
There are 5 test cases presented in this directory, each is to compare the USGS's modpath version 6 with alternative particle traking solutions.

## Test Case 1
Test case 1 utilizes flopy and modpath6 to reproduce figure 7 in Pollock 1988

![alt text](https://github.com/rosskush/pollock_88_modpath/blob/master/Test_Case_1/fig7.PNG)

Particles are placed radially around the well cell in the bottom left corner and are tracked for 7,500 days.

![alt text](https://github.com/rosskush/pollock_88_modpath/blob/master//Test_Case_1/output/figures/7500_days.png)

To run this example follow these steps in a terminal or Anaconda prompt after moving to this directory:

(if not active already, activate the modpath_qa conda enviroment):
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

![alt text](https://github.com/rosskush/pollock_88_modpath/blob/master//Test_Case_2/output/figures/30pt0_days.png)

To run this example follow these steps in terminal or Anaconda prompt after moving to this directory:

(if not active already, activate the modpath_qa conda enviroment):
```
source activate modpath_qa
cd Test_Case_2
./runme.bat
```
This will produce a directory called output that plot figures and pass/fail statistics will be placed.


## Test Case 3
Test Case 3 compares an analytical well capture zone solution described by Grubb in 1993 to the results from a backwards particle track in modpath6, this example assumes a homgenous unconfined system with a single extraction well.

![alt text](https://github.com/rosskush/pollock_88_modpath/blob/master//Test_Case_3/output/backwards.png)


To run this example follow these steps in a terminal or Anaconda prompt after moving to this directory:

(if not active already, activate the modpath_qa conda enviroment):
```
source activate modpath_qa
cd Test_Case_3
./runme.bat
```
This will produce a directory called output that plot figures and pass/fail statistics will be placed.




