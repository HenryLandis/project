#!/usr/bin/env python

"""
The main API interface
"""

from sproc.fetch import Fetch
from sproc.jsonify import GeographicRange
from sproc.imap import IMap


class Sproc:
    def __init__(self, species, workdir=".", scalar=2.5):
        # Store inputs.
        self.species = species
        self.workdir = workdir

        # Placeholders for dataframe, shapely [Multi]Polygon, folium map.
        self.data = None
        self.georange = None
        self.map = None

        # Number of occurrences for species.
        self.occs = None

        # Generate results.
        self._run(scalar)


    def _run(self, outlier_scalar):
        """
        Run internal functions.
        """
        records = Fetch(species = self.species)
        georange = GeographicRange(
            data = records.data, 
            name = self.species,
            workdir = self.workdir,
            scalar = outlier_scalar,
        )
        self.data = georange.data
        self.georange = georange.georange
        self.map = IMap(georange.json_file).imap
        self.occs = self.data.shape[0]


    def __repr__(self):
        _data = [
            "<Sproc ",
            f"spp = '{self.species}', ",
            f"occs = {self.data.shape[0]}, ",
            f"range_area = {self.georange.area:.2f}/>",
        ]
        return "".join(_data)