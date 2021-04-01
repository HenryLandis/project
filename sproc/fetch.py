#!/usr/env/bin python

"""
Fetch occurrence records from GBIF REST API.
"""

import pandas as pd
import pygbif
from loguru import logger


# TODO: add the load GeoJSON function back? May allow users to more easily constrain to points in accepted range.


class Fetch:
    """
    A class object to store data on species occurrence from GBIF.  
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
        GBIF REST API caller.
        """
        
        # Get usage key for the queried species.
        species_key = pygbif.species.name_backbone(
            name = self.species,
            rank = 'species',
        )['usageKey']

        # Run a while-loop to go through all observations.  
        data = []
        curr_offset = 0
        while 1:
           
            # Make API request.
            occ_records = pygbif.occurrences.search(
                taxonKey = species_key, 
                hasCoordinate = True,
                offset = curr_offset,
                **self.kwargs
            )

            # Store JSON array.
            if occ_records:
                data.extend(occ_records['results'])

            # Check if querying is finished.
            if not occ_records['endOfRecords']:
                curr_offset += occ_records['limit']

            else:
                break
        
        # Normalize data.
        self.data = pd.json_normalize(data)

        # Subset key columns.
        self.data = self.data[[
            "key", 
            "speciesKey",
            "species",
            "decimalLatitude",
            "decimalLongitude",
        ]]

        # Drop duplicates.
        self.data = self.data.drop_duplicates().reset_index(drop = True)
        
        return self.data