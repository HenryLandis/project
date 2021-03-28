#!/usr/bin/env python

"""
The main API interface
"""

from sproc.fetch import Fetch
from sproc.jsonify import GeographicRange
from sproc.imap import Map


class Sproc:
    def __init__(self, species, workdir=".", scalar=2.5):
        # store inputs
        self.species = species
        self.workdir = workdir

        # to be filled (dataframe, shapely [Multi]Polygon, folium map)
        self.data = None
        self.georange = None
        self.map = None

        # generate results
        self._run(scalar)


    def _run(self, outlier_scalar):
        """
        Run internal functions
        """
        records = Fetch(species=self.species)
        georange = GeographicRange(
            data=records.data, 
            name=self.species,
            workdir=self.workdir,
            scalar=outlier_scalar,
        )
        self.data = records.data
        self.georange = georange.georange
        self.map = Map(georange.json_file).imap


    def __repr__(self):
        _data = [
            "<Sproc ",
            f"spp='{self.species}', ",
            f"occs={self.data.shape[0]}, ",
            f"range_area={self.georange.area:.2f}/>",
        ]
        return "".join(_data)
