# README #

Python scripts for building modflow and modpath models from Polluck 1988 

## Installation notes

Following this tutorial will require recent installations of:
=======
- Python >= 3.6.5
- pandas
- geopandas >= 0.4.0
- matplotlib
- flopy >= 3.2.9 
- numpy

If you do not yet have these packages installed, we recommend to use the [conda](http://conda.pydata.org/docs/intro.html) package manager to install all the requirements 
(you can install [miniconda](http://conda.pydata.org/miniconda.html) or install the (larger) Anaconda
distribution, found at https://www.anaconda.com/download/).

Once this is installed, the following command will install all required packages in your Python environment:
(this may take a bit)
```
conda env create -f environment.yml
```

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

To run this example follow these steps in terminal or bash after moving to this directory:

(if not active already, activate the modpath_qa conda enviroment):
```
source activate modpath_qa
cd Test_Case_1
./runme.bat
```
This will produce a directory called output that plot figures and pass/fail statistics will be placed.

## Test Case 2
Test case 2 utilizes flopy and modpath6 to reproduce figure 10 in Pollock 1988

![alt text](https://github.com/rosskush/pollock_88_modpath/blob/master/Test_Case_2/fig10.PNG)

Particles are placed radially around the well cell in the bottom left corner and are tracked for 7,500 days.

![alt text](https://github.com/rosskush/pollock_88_modpath/blob/master//Test_Case_2/output/30pt0_days.png)

To run this example follow these steps in terminal or bash after moving to this directory:

(if not active already, activate the modpath_qa conda enviroment):
```
source activate modpath_qa
cd Test_Case_2
./runme.bat
```
This will produce a directory called output that plot figures and pass/fail statistics will be placed.
