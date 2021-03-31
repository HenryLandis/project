#!/usr/env/bin python

"""
GeoJSON records for SPROC
"""

import os
import numpy as np
import shapely
from loguru import logger
import geojson
from sproc.globals import LAND



class GeographicRange:
    """
    Writes CSV records to a GeoJSON format.
    """
    def __init__(self, data, name="test", workdir=".", scalar=3):

        self.data = data.reset_index()
        self.name = name
        self.workdir = workdir
        self.json_file = (
            os.path.join(self.workdir, self.name + ".json")
            .replace(" ", "_")
        )
        self.points = list(zip(data.decimalLongitude, data.decimalLatitude))
        self.feature_collection = geojson.FeatureCollection(
            features=[],
            properties={"name": name},
        )

        # results to get and store to JSON
        self.georange = None

        # run the steps
        self._mark_outliers(scalar)
        self._add_points()
        self._add_polygon()
        self.write()


    @property
    def center(self):
        "Get the center of the geographic range"
        return self.georange.centroid.xy[0][0], self.georange.centroid.xy[1][0]


    def _mark_outliers(self, scalar=3):
        """
        A point is an outlier if it is >3 std euclidean dist from the
        median lat,long of all points.
        """
        # columns to fill
        self.data["outlier_distance"] = 0.
        self.data["outlier_status"] = False

        # median coordinate
        origin = shapely.geometry.Point(
            self.data.decimalLongitude.median(), 
            self.data.decimalLatitude.median()
        )

        # get distances
        for idx in self.data.index:
            point = shapely.geometry.Point(self.points[idx])
            self.data.loc[idx, "outlier_distance"] = point.distance(origin)

        # Adds 1e-7 to prevent dist=0
        self.data["outlier_distance"] += 1e-7

        # label as outlier if >3 STD. 
        cutoff = np.log(self.data["outlier_distance"]).std() * scalar
        mask = np.log(self.data["outlier_distance"]) >= cutoff
        self.data.loc[mask, "outlier_status"] = True
        logger.info(f"dropped outliers: {mask.sum()}")


    def _add_points(self):
        """
        store all of the observed point occurrences.
        """
        for idx in self.data.index:

            # get data
            key = self.data.loc[idx, "key"]
            uri = f"https://www.gbif.org/occurrence/{key}"
            outlier = str(self.data.loc[idx, "outlier_status"]).lower()
            longitude = self.data.loc[idx, "decimalLongitude"]
            latitude = self.data.loc[idx, "decimalLatitude"]
            point = (longitude, latitude)
            geometry = geojson.Point(coordinates=point)

            # write as a feature
            feature = geojson.Feature(
                geometry=geometry, 
                properties={
                    "type": "occurrence",
                    "record": f"<a href={uri} target='_blank'>{uri}</a>",
                    "outlier": outlier,
                    }
            )
            self.feature_collection['features'].append(feature)
        

    def _add_polygon(self):
        """
        Computes polygon, removes water bodies, and stores.
        """
        # get filtered points without outliers
        fpoints = list(zip(
            self.data.loc[~self.data.outlier_status, "decimalLongitude"], 
            self.data.loc[~self.data.outlier_status, "decimalLatitude"], 
        ))

        # get the convex hull around points
        rawpoly = shapely.geometry.Polygon(fpoints)
        conv_hull = rawpoly.convex_hull

        # get intersection with global LAND
        clean_hull = conv_hull.intersection(LAND)

        # store this [Multi]Polygon as the geographic range
        self.georange = clean_hull

        # if it is a sinle polygon then write it.
        if clean_hull.geom_type == "Polygon":
            outline = clean_hull.boundary.coords
            coords = list(zip(outline.xy[0], outline.xy[1]))
            geometry = geojson.Polygon(coordinates=[coords], validate=True)
            feature = geojson.Feature(
                geometry=geometry, properties={"type": "geographic_range"})

        # if multipolygon then add each bit by bit
        elif clean_hull.geom_type == "MultiPolygon":
            geometry = geojson.MultiPolygon()
            for poly in clean_hull:
                coords = list(zip(
                    poly.boundary.coords.xy[0], 
                    poly.boundary.coords.xy[1],
                ))
                subgeometry = geojson.Polygon([coords], validate=True)
                geometry.coordinates.append(subgeometry.coordinates)
            feature = geojson.Feature(
                geometry=geometry, properties={"type": "geographic_range"})
        else:
            raise ValueError(f"odd shaped hull error: {clean_hull.geom_type}")
        self.feature_collection['features'].append(feature)
    

    def write(self):
        """
        Writes feature collection to GeoJSON file.
        """
        if not os.path.exists(self.workdir):
            os.makedirs(self.workdir)

        # write to JSON
        with open(self.json_file, 'w') as outf:
            outf.write(geojson.dumps(self.feature_collection, indent=4))
        logger.info(f"wrote data to {self.json_file}")
