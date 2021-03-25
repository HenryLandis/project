#!/usr/bin/env python

from pygbif import species
from pygbif import occurrences as occ
import numpy as np
import os
import pandas as pd
from scipy import stats
import shapely


class Sproc:
    """
    A class object to store data on species occurrence from gbif.  Users supply a species
    name and optionally a selection of other parmeters.
    """
    # lat: north/south, y
    # lon: east/west, x

    def __init__(self,
    sp_name,
    basis = True,
    continent = None,
    lat_range = None,
    lon_range = None,
    outdir = None
    ):

        # Create a dict object to store parameters for setting up gbif queries.
        self.params = {}

        # Build dict.  For optional params, set if provided or set as None if not.
        self.params['spname'] = sp_name
        self.params['basis'] = basis
        if continent:
            self.params['continent'] = continent
        else:
            self.params['continent'] = None
        if lat_range:
            _ = np.sort(lat_range)
            self.params['ymin'] = _[0]
            self.params['ymax'] = _[1]
        else:
            self.params['ymin'] = None
            self.params['ymax'] = None
        if lon_range:
            _ = np.sort(lon_range)
            self.params['xmin'] = _[0]
            self.params['xmax'] = _[1]
        else:
            self.params['xmin'] = None
            self.params['xmax'] = None
    
        # Set outdir if provided, otherwise defaults to current working directory.
        if outdir:
            self.outdir = os.path.realpath(os.path.expanduser(outdir))
        else:
            self.outdir = os.path.expanduser(os.path.curdir)
        
        # Set a geometry attribute.
        self.geometry = None


    def get_shapefile(self):
        """
        Retrieves a locally saved shapefile for the species specified by the class instance,
        if the file is available.
        """

        import geopandas as gpd

        # Build the filepath to the expected shapefile.
        filepath = "../shapefiles/" + self.params['spname'].replace(" ", "_") + ".shp"

        # If the filepath exists, save the shapefile to the class instance.
        if os.path.exists(filepath) == True:
            self.geometry = gpd.read_file(filepath)
            print("Saved local shapefile to class instance.")

        # If not, raise an error.
        else:
            print("No local shapefile available for this species.")



    def get_gbif_occs(self, geometry = False, tol = 0):
        """
        Query the gbif database for occurrence data.
        """

        # Create a file to store occurrence data.
        self.occfile = os.path.join(self.outdir, self.params['spname'].replace(" ", "_") + ".csv")

        # Get the usageKey for species of interest.
        self.key = species.name_backbone(name = self.params['spname'], rank = 'species')['usageKey']

        # Create latitude/longitude lists.
        self.lats = []
        self.lons = []

        # Build dicts for optional params.
        # if self.params['basis'] == True:
        basis_params = dict(
            basisOfRecord = ['HUMAN_OBSERVATION', 'LIVING_SPECIMEN', 'FOSSIL_SPECIMEN'],
        )
        # if self.params['continent'] is not None:
        continent_params = dict(
            continent = self.params['continent']
        )
        if geometry == True:
            geo_orient = shapely.geometry.polygon.orient(self.geometry['geometry'][0], 1.0) # Counter-clockwise for GBIF.
            geometry_bounds = dict(
                geometry = str(geo_orient.simplify(tol))
            )
        else:
            geometry_bounds = dict(place = 'holder')
        search_bounds = dict(
            decimalLatitude = ','.join([str(self.params['ymin']), str(self.params['ymax'])]),
            decimalLongitude = ','.join([str(self.params['xmin']), str(self.params['xmax'])]),
        )

        # Run a while-loop to go through all observations.  By default, tries to narrow to native range.
        # Don't pass lat/long bounds if none were entered.
        curr_offset = 0
        end_records = False
        while not end_records:
            occ_records = occ.search(taxonKey = self.key, 
            hasCoordinate = True,
            # hasGeospatialIssue = False,
            **{k: v for k, v in basis_params.items() if self.params['basis'] == True},
            **{k: v for k, v in continent_params.items() if self.params['continent'] is not None},
            **{k: v for k, v in geometry_bounds.items() if geometry == True},
            **{k: v for k, v in search_bounds.items() if 'None' not in v},
            offset = curr_offset
            )
            end_records = occ_records['endOfRecords']
            curr_offset += occ_records['limit']

            # Add latitude/longitude results to lists.
            self.lats.extend([i['decimalLatitude'] for i in occ_records['results']])
            self.lons.extend([i['decimalLongitude'] for i in occ_records['results']])

            # Print a dot on each cycle to show progress.
            print(".", end = "")

            # When end of data is reached: build pandas dataframe from lists and remove duplicate data points.
            if occ_records['endOfRecords']:
                df = pd.DataFrame({'Latitude': self.lats, 'Longitude': self.lons})
                df = df.drop_duplicates().reset_index()
                df = df.drop('index', axis = 1)

                # Filter outliers.
                df = df[(np.abs(stats.zscore(df)) < 3).all(axis=1)]

                # Reform the lists by subsetting the dataframe.
                self.lats = list(df['Latitude'])
                self.lons = list(df['Longitude'])

                # Print final number of records.
                print(f' Found {len(self.lats)} records.')

        # Build array to write to CSV file.  np.vstack layers arrays vertically, where each layer is species-lat-lon.  
        # np.repeat copies the species names as many times as there are entries.  It also combines with zip() to put
        # a newline char at the end of each layer.
        csvarr = np.vstack([np.repeat(self.params['spname'].replace(" ", "_"), len(self.lats)), self.lats,
                ["{}{}".format(a_, b_) for a_, b_ in zip(self.lons, np.repeat('\n', len(self.lats)))]]
                ).T

        # Write array to CSV file.
        with open(self.occfile, 'w') as f:
            f.write('Species,Latitude,Longitude\n')
            for line in csvarr:
                f.write(",".join(line))

        # Transform lists to arrays for downstream application.
        self.lats = np.array(self.lats)
        self.lons = np.array(self.lons)
        

    def run(self, geometry = False, tol = 0):
        """
        Simple command to save occurrence data to class object.
        """

        # If the specified outdir doesn't exist, make it.
        if os.path.exists(self.outdir) == False:
            os.mkdir(self.outdir)

        # Get occurrence data.
        self.get_gbif_occs(geometry = geometry, tol = tol)


    def write_shapefile(self):
        """
        Build and save a shapefile from retrieved points.
        """

        from shapely.geometry import Polygon
        import shapefile

        # Build a list lat/lon pairs from retrieved points.
        points = [[lat, lon] for lat, lon in zip(self.lats, self.lons)]

        # Build a convex hull from the points, then orient the points clockwise for writing to shapefile.
        poly = Polygon(points).convex_hull
        poly_orient = shapely.geometry.polygon.orient(poly, -1.0)

        # Rearrange exterior coords from the oriented convex hull into long/lat (XY).  This is because 
        # GBIF requires a geometry argument in WKT, which is an XY format.
        wpoints = [[lon, lat] for lon, lat in zip(poly_orient.exterior.coords.xy[1], poly_orient.exterior.coords.xy[0])]

        # Write to shapefile.  Can load with get_shapefile() if desired.
        with shapefile.Writer(os.path.join("../shapefiles", self.params['spname'].replace(" ", "_")), shapeType = 5) as w:
            w.field('poly', 'C')
            w.poly([wpoints])
            w.record("polygon1")