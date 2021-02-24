# Project

Outline of project concept for quantifying the overlap in species ranges based on occurrence data.  (Tentative name idea: *sproc - SPecies Range Overlap Calculator*)

## Proposed goal

Provide an API interface for:
- Querying occurrence data (from GBIF, maybe other sources).  Parameters include taxonomic names (species, genus, etc), latitude/longitude, and other options provided by the database.
- Drawing species ranges using a convex hull approach.
- Multiple approaches to visualizing occurrence density (square vs. hex bins, thresholds, etc)
- Quantifying overlap between two ranges (output may vary depending on density formatting).

## Proposed code
- ``pygbif`` is a Python wrapper around the GBIF REST API.
- ``geopandas`` provides tools for constructing polygons and defining overlap.
- ``maxent`` is a Java tool for modeling species niches and distributions.  ``smood`` builds on ``maxent`` to visualize these distributions.
- ``numpy`` and ``pandas`` will likely have applications in data manipulation and presentation.
- ``NichePy`` is another package to estimate niche and distribution overlap.

Several published articles describe methods to calculate range overlap for plant species, relying on R packages [(Anacker & Strauss 2014,](https://royalsocietypublishing.org/doi/10.1098/rspb.2013.2980) [Cardillo & Warren 2016,](https://onlinelibrary.wiley.com/doi/full/10.1111/geb.12455), [Junker et al. 2016).](https://besjournals.onlinelibrary.wiley.com/doi/full/10.1111/2041-210X.12611)  Their approaches may serve as additional inspiration.

## Description of data
Data will be accessed programatically from GBIF using its REST API framework.

## User interaction
Because the proposed goals are heavily intertwined with mapping, users would likely preferto interact with the package through an API, for example in Jupyter notebooks.
