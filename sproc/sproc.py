#!/usr/bin/env python

from pygbif import species
from pygbif import occurrences as occ
import numpy as np
import os

"""
For now: using this space to note things that might be useful.

PACKAGES:
pygbif, specifically import occ and species to get useful queries.  Start with only getting species name and lat/lon range.
geopandas (and its dependencies) do all the plotting.

CLASS OBJECTS:
Start with one central object for querying gbif and saving data.  Ideally a single run() function can handle stuff.
The API will place a limit on simultaneous queries, so I'll need to use the cycling trick to get however many (300?) at a time.
The data that should be saved are a list of lat/lon.

I don't expect to use Maxent at this time, so I don't need to do reformatting to account for that.  geopandas is another story,
but of course I plan to use that quite a bit.

FUNCTIONS:
In a utils.py folder, build mapping functions.  pyplot.hexbin and pyplot.hist2d can do hex and squared binning respectively.
KDE may be useful visually but not quantitatively.

Quantifying overlap is different than qualitatively visualizing it.  Within geopandas, the centrography packagage can compute
convex hulls, and the descartes.PolygonPatch class object does alpha shapes.  gbif coordinates plus projection are needed:
use WGS84 (EPSG: 4326) because the gbif data uses that.
geopandas.overlay() does the geometry that I expect to calculate the final values (intersection).  Hopefully it takes two
convex hulls or alpha shapes as arguments, if not some transforming may be necessary.  All of this should be wrapped in a 
single "get overlay" function.

Is it also possible to overlay hex/square bin maps, and quantify that in a meaningful way?

"""

class Sproc:
    """
    A class object to store data on species occurrence from gbif.  Users supply a species name, latitude/longitude range,
    and a directory for saving the output in CSV format.
    """
    # lat: north/south, y
    # lon: east/west, x

    def __init__(self,
    sp_name = None,
    lat_range = None,
    lon_range = None,
    outdir = None
    ):

        # Create a dict object to store parameters for gbif query.
        self.params = {}

        # Build dict.  Include params if provided, otherwise set as None.
        if sp_name:
            self.params['spname'] = sp_name
        else:
            self.params['spname'] = None
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


    def get_gbif_occs(self):
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

        # Run a while-loop to go through all observations.  TODO: ignore duplicates.
        curr_offset = 0
        end_records = False
        while not end_records:
            occ_records = occ.search(taxonKey = self.key, hasCoordinate = True, 
            decimalLatitude = ','.join([str(self.params['ymin']), str(self.params['ymax'])]),
            decimalLongitude = ','.join([str(self.params['xmin']), str(self.params['xmax'])]),
            offset = curr_offset
            )
            end_records = occ_records['endOfRecords']
            curr_offset += occ_records['limit']

            # Add latitude/longitude results to lists.
            self.lats.extend([i['decimalLatitude'] for i in occ_records['results']])
            self.lons.extend([i['decimalLongitude'] for i in occ_records['results']])

            # Print a dot on each cycle to show progress.
            print(".", end = "")

            # When end of data is reached, print length of final results.
            if occ_records['endOfRecords']:
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
        

    def run(self):
        """
        Simple command to save occurrence data to class object.
        """

        # If the specified outdir doesn't exist, make it.
        if os.path.exists(self.outdir) == False:
            os.mkdir(self.outdir)

        # Get occurrence data.
        self.get_gbif_occs()


