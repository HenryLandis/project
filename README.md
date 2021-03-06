# sproc

``sproc`` is a Python package with the objective of visualizing and quantifying the overlap between the ranges of two taxa as determined by latitude/longitude occurrence data.



### In development...

The list of dependencies required by ``sproc`` are:

- ``pygbif``
- ``numpy``
- ``pandas``
- ``geopandas``
- ``matplotlib``
- ``contextily``
- ``seaborn``
- ``libpysal``

The following command in ``conda`` installs these packages if not already installed:

```conda install pygbif numpy pandas geopandas matplotlib contextily seaborn libpysal -c conda-forge```

Currently, ``sproc`` can only be installed locally.  Use the following commands to clone this repository to your local machine:

```
git clone https://github.com/HenryLandis/sproc.git
cd ./sproc
pip install -e .
```
