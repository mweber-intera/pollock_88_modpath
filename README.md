# README #

Python scripts for building modflow and modpath models from Polluck 1988 

"Semianalytical Computation of Path Lines for Finite-Difference Models"


## Installation notes

Following this tutorial will require recent installations of:

- Python >= 3.6
- pandas
- geopandas >= 0.3.0
- matplotlib
- flopy >= 3.2.9 
- numpy

If you do not yet have these packages installed, we recommend to use the [conda](http://conda.pydata.org/docs/intro.html) package manager to install all the requirements 
(you can install [miniconda](http://conda.pydata.org/miniconda.html) or install the (larger) Anaconda
distribution, found at https://www.anaconda.com/download/).

Once this is installed, the following command will install all required packages in your Python environment:

```
conda env create -f environment.yml
```


# Test Cases #
There are 5 test cases presented in this directory, each is to compare the USGS's modpath version 6 with alternative particle traking solutions.

## Test Case 1
Test case 1 utilizes flopy and modpath6 to reproduce figure 7 in Pollock 1988

![alt text](https://github.com/rosskush/pollock_88_modpath/blob/master/Test_Case_1/fig7.PNG)

Particles are placed radially around the well cell in the bottom left corner and are tracked for 7,500 days.

![alt text](https://github.com/rosskush/pollock_88_modpath/blob/master//Test_Case_1/figures/7500_days.png)
