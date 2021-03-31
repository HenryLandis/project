#!/usr/env/bin python

"""
Fetch occurrence records from GBIF REST API
"""

import pandas as pd
import pygbif
from loguru import logger


class Fetch:
    """
    A class object to store data on species occurrence from gbif.  
    Users supply a species name and optionally a selection of other
    parmeters.
    
    Parameters
    ----------
    sp_name: str
        ...
    """
    def __init__(
        self, 
        species, 
        kwargs = {
            'basisOfRecord': 'PRESERVED_SPECIMEN',            
            }
        ):
        self.species = species
        self.data = pd.DataFrame([])
        self.kwargs = kwargs
        self.request()
        logger.info(f"fetched {self.data.shape[0]} occurrence records")


    def request(self):
        """
        GBIF REST API caller
        """
        # get usage key for the queried species
        species_key = pygbif.species.name_backbone(
            name=self.species,
            rank='species',
        )['usageKey']

        # build a dict for other search kwargs
        #kwargs = {
            #'basisOfRecord': 'PRESERVED_SPECIMEN',            
            # 'basisOfRecord': 'HUMAN_OBSERVATION',
        #}

        # Run a while-loop to go through all observations.  
        data = []
        curr_offset = 0
        while 1:
           
            # make an API request
            occ_records = pygbif.occurrences.search(
                taxonKey=species_key, 
                hasCoordinate=True,
                offset=curr_offset,
                **self.kwargs
            )

            # store JSON array
            if occ_records:
                data.extend(occ_records['results'])

            # check if finished.
            if not occ_records['endOfRecords']:
                curr_offset += occ_records['limit']

            else:
                break

        self.data = pd.json_normalize(data)
        self.data = self.data[[
            "key", 
            "speciesKey",
            "species",
            "decimalLatitude",
            "decimalLongitude",
        ]]
        return self.data
