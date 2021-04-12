# sproc (SPecies Range Overlap Calculator)

``sproc`` is a Python package with the objective of visualizing and quantifying the overlap between the ranges of two taxa as determined by latitude/longitude occurrence data.

### In development...

The following is a list of dependencies required by the ``sproc`` core querying functionality:

- ``pygbif``
- ``numpy``
- ``pandas``
- ``loguru``
- ``shapely``
- ``geojson``

For ``sproc`` mapping functionality, the following package is required:

- ``geopandas``

Additionally required for static mapping:

- ``matplotlib``
- ``contextily``
- ``seaborn``

Additinally required for interactive mapping:

- ``folium``

Use the following conda syntax to install any dependencies you need:

```
conda install [pygbif numpy pandas ...] -c conda-forge
```

If you would like to contribute to the development of ``sproc``, use the following commands to clone this repository to your local machine:

```
git clone https://github.com/HenryLandis/sproc.git
cd ./sproc
pip install -e .
```

### Working example

Read the [working example notebook](https://nbviewer.jupyter.org/github/HenryLandis/sproc/blob/main/notebooks/working-example.ipynb) for an overview of the ``sproc`` workflow and functionality.
