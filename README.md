# README #

Python scripts for building modflow and modpath models from Polluck 1988 

"Semianalytical Computation of Path Lines for Finite-Difference Models"

![alt text](https://github.com/rosskush/pollock_88_modpath/blob/master/figures/final_gif.gif)



## Installation notes

Following this tutorial will require recent installations of:

- Python >= 3.5 (it will probably work on python 2.7 as well, but I didn't test it specifically)
- pandas
- geopandas >= 0.3.0
- matplotlib
- rtree
- PySAL
- scikit-learn
- mgwr
- cartopy
- geoplot
- [Jupyter Notebook](http://jupyter.org)

If you do not yet have these packages installed, we recommend to use the [conda](http://conda.pydata.org/docs/intro.html) package manager to install all the requirements 
(you can install [miniconda](http://conda.pydata.org/miniconda.html) or install the (larger) Anaconda
distribution, found at https://www.anaconda.com/download/).

Once this is installed, the following command will install all required packages in your Python environment:

```
conda env create -f environment.yml
```

But of course, using another distribution (e.g. Enthought Canopy) or ``pip`` is fine as well (a requirements file is provided as well), as long as you have the above packages installed.




