# sproc (SPecies Range Overlap Calculator)

``sproc`` is a Python package with the objective of visualizing and quantifying the overlap between the ranges of two taxa as determined by latitude/longitude occurrence data.

### In development...

The list of dependencies required by ``sproc`` are:

- ``pygbif``
- ``numpy``
- ``pandas``
- ``scipy``
- ``geopandas``
- ``matplotlib``
- ``contextily``
- ``seaborn``
- ``shapely``
- ``libpysal``

The following command in ``conda`` installs these packages if not already installed:

```
conda install pygbif numpy pandas scipy geopandas matplotlib contextily seaborn shapely libpysal -c conda-forge
```

Currently, ``sproc`` can only be installed locally.  Use the following commands to clone this repository to your local machine:

```
git clone https://github.com/HenryLandis/sproc.git
cd ./sproc
pip install -e .
```

### Working example

The class object ``Sproc`` handles the formatting of queries to the Global Biodiversity Information Facility (GBIF) database.  At minumum, the user must supply a scientific species name.  By default, the parameter ``basis = True`` constrains the query to only retrieve live observations of the species.

The function ``Sproc.run()`` submits the query to the GBIF REST API and returns a CSV file with three columns: species name, latitude and longitude.  This file can be used as input for downstream utility functions (or alternatively, the user may supply pre-formatted latitude and longitude data from a different preferred source).

Optional parameters for the class object include:
- ``continent``: constrain the query to observations on a continent or list of continents.  This can help to filter observations of species that have been introduced to areas outside their native range.
- ``lat_range`` and ``lon_range``: define latitude and longitude bounds for the query.
- ``outdir``: specify a directory for the CSV file formatted from the query output.  If left blank, defaults to the user's current directory.

The following example demonstrates retreving live occurrence data from GBIF for *Quercus rubra,* the red oak, within a subset of its native range in eastern North America.

```
from sproc import Sproc
QR = Sproc("Quercus rubra", basis = True, lat_range = [40, 45], lon_range = [-100, -80],
           outdir = "/home/henrylandis/sproc")
QR.run()

....... Found 1783 records.
```

Inspecting the output:

```
import pandas as pd
df = pd.read_csv("/home/henrylandis/sproc/Quercus_rubra.csv")
df.head()
```

| Species       | Latitude  | Longitude  |
|---------------|-----------|------------|
| Quercus_rubra | 44.63798  | -92.894133 |
| Quercus_rubra | 41.500608 | -87.80316  |
| Quercus_rubra | 40.689503 | -81.981554 |
| Quercus_rubra | 41.677495 | -87.899514 |
| Quercus_rubra | 40.135042 | -84.45143  |

The utility functions provide a variety of options for visualizing occurrence data and geometric ranges.  These include:
- ``hexmap``: a hex-based grid map with adjustable hex size.
- ``recmap``: a rectangle (or square) grid map with adjustable box size.
- ``kdemap``: a Kernel Density Estimation (KDE) of occurrence data, showing occurrence data as a probability density function.
- ``plot_polygons_intersection``: determine and plot the geometric polygon representing the intersection of two species ranges.
- ``plot_polygons_separate``: plot two species ranges either side-by-side or overlaid on one figure.
- ``world_plot``: plot occurrence points for one or two taxa on a world map.

In the following example, we perform a second query on *Quercus palustris,* the pin oak, also native to eastern North America; we then use ``plot_polygons_separate`` to visualize the ranges of *Q. rubra* and *Q. palustris* separately, as well as overlaid on one figure.

```
QP = Sproc("Quercus palustris", basis = True, lat_range = [40, 45], lon_range = [-100, -80],
           outdir = "/home/henrylandis/sproc")
QP.run()

.. Found 467 records.
```

```
from sproc import utils
utils.plot_polygons_separate("/home/henrylandis/sproc/Quercus_rubra.csv", 
                             "/home/henrylandis/sproc/Quercus_palustris.csv",
                            label1 = "Quercus rubra", label2 = "Quercus palustris", sep = True, legend = True, 
                            figsize = (50, 50), fontsize = 40, markerscale = 25)
```

![](https://gyazo.com/baf0a98416c0527abbc01ea50c4aefbe.jpg)

```
utils.plot_polygons_separate("/home/henrylandis/sproc/Quercus_rubra.csv", 
                             "/home/henrylandis/sproc/Quercus_palustris.csv",
                            label1 = "Quercus rubra", label2 = "Quercus palustris", sep = False, legend = True, 
                            figsize = (50, 50), fontsize = 40, markerscale = 25)
```

![](https://i.gyazo.com/a2c6d068eb014d2a306065ae8bde4338.jpg)




