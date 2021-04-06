#!/usr/bin/env python

import pandas as pd
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.cm as cm
import numpy as np


# Make dataframes have wider columns for neatness.
pd.set_option("max_colwidth", 14)


class SingleSMap:
    """
    Class for static mapping of occurrence data for a single taxon with matplotlib/contextily.
    """

    def __init__(self, json_file):
        self.json_file = json_file
        # self.name = os.path.basename(self.json_file).rsplit(".json")[0]
        self.data = gpd.read_file(json_file)


    def hexmap(self, figsize = (12, 9), gridsize = 10, alpha = 0.5, cmap = 'viridis_r'):
        """
        Build a hex-based grid map from arrays of latitude/longitude occurrence data.
        The gridsize parameter controls the size of the hexaognal "bins" of point data.
        """

        # Subset non-outlier occurrence points.
        gdf = self.data[(self.data["type"] == "occurrence") & (self.data['outlier'] == "false")]
        gdf = gdf.reset_index(drop = True)

        # Set up figure and axis.
        f, ax = plt.subplots(1, figsize = figsize)

        # Generate and add hexbins.
        ax.hexbin(
            [gdf['geometry'][idx].coords.xy[0] for idx in gdf.index], # x
            [gdf['geometry'][idx].coords.xy[1] for idx in gdf.index], # y
            gridsize = gridsize,
            linewidths = 0,
            alpha = alpha,
            cmap = 'viridis_r'
        )

        # Add basemap, converting tilemap from Web Mercator to WGS84.
        cx.add_basemap(
            ax,
            crs = gdf.crs.to_string(),
            source = cx.providers.OpenStreetMap.Mapnik
        )

        # Add colorbar, forcing it to match figure size.
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size = "5%", pad = 0.1)
        plt.colorbar(cm.ScalarMappable(norm = None, cmap = cmap), ax = ax, cax = cax)

        # Remove axes.
        # ax.set_axis_off()


    def recmap(self, figsize = (12, 9), bins = 10, cmin = None, cmax = None, alpha = 0.5, cmap = 'viridis_r'):
        """
        Build a rectangle-based grid map from latitude/longitude occurrence data.
        Bins can be specified as a single integer to produce equal bins in two
        dimensions (a square), or a list of two integers [int, int]
        to create rectangular binning.
        """

        # Subset non-outlier occurrence points.
        gdf = self.data[(self.data["type"] == "occurrence") & (self.data['outlier'] == "false")]
        gdf = gdf.reset_index(drop = True)

        # Set up figure and axis.
        f, ax = plt.subplots(1, figsize = figsize)

        # Generate and add 2D histogram.
        ax.hist2d(
            np.concatenate([gdf['geometry'][idx].coords.xy[0] for idx in gdf.index]), # x
            np.concatenate([gdf['geometry'][idx].coords.xy[1] for idx in gdf.index]), # y
            bins = bins,
            cmin = cmin,
            cmax = cmax,
            alpha = alpha,
            cmap = cmap,
        )

        # Add basemap, converting tilemap from Web Mercator to WGS84.
        cx.add_basemap(
            ax,
            crs = gdf.crs.to_string(),
            source = cx.providers.OpenStreetMap.Mapnik
        )

        # Add colorbar, forcing it to match figure size.
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size = "5%", pad = 0.1)
        plt.colorbar(cm.ScalarMappable(norm = None, cmap = cmap), ax = ax, cax = cax)

        # Remove axes.
        # ax.set_axis_off()


    def kdemap(self, figsize = (12, 9), levels = 50, alpha = 0.5, cmap = 'viridis_r'):
        """
        Build a map of kernel density estimation from latitude/longitude occurrence data.  
        levels controls the degree of gradient shading.
        """

        import seaborn as sns
        
        # Subset non-outlier occurrence points.
        gdf = self.data[(self.data["type"] == "occurrence") & (self.data['outlier'] == "false")]
        gdf = gdf.reset_index(drop = True)

        # Set up figure and axis.
        f, ax = plt.subplots(1, figsize = figsize)

        # Generate and add KDE map.
        sns.kdeplot(
            np.concatenate([gdf['geometry'][idx].coords.xy[0] for idx in gdf.index]), # x
            np.concatenate([gdf['geometry'][idx].coords.xy[1] for idx in gdf.index]), # y
            n_levels = levels,
            shade = True,
            alpha = alpha,
            cmap = cmap
        )

        # Add basemap, converting tilemap from Web Mercator to WGS84.
        cx.add_basemap(
            ax,
            crs = gdf.crs.to_string(),
            source = cx.providers.OpenStreetMap.Mapnik
        )

        # Add colorbar, forcing it to match figure size.
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size = "5%", pad = 0.1)
        plt.colorbar(cm.ScalarMappable(norm = None, cmap = cmap), ax = ax, cax = cax)

        # Remove axes.
        # ax.set_axis_off()


    def worldmap(self, figsize = (30, 30)):
        """
        View worldwide occurrence data on a simple static map.
        """

        # Get world map from geopandas.
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        world = world[(world.pop_est > 0) & (world.name != "Antarctica")]
        base = world.plot(color = 'white', edgecolor = 'black', figsize = figsize)

        # Subset non-outlier occurrence points.
        gdf = self.data[(self.data["type"] == "occurrence") & (self.data['outlier'] == "false")]
        gdf = gdf.reset_index(drop = True)

        # Plot occurrence data.
        gdf.plot(ax = base, marker = 'o', color = 'red', markersize = 2)


class MultiSMap:
    """
    Class for static mapping of occurrence data for multiple taxa with matplotlib/contextily.
    """

    def __init__(self, json_files):
                
        # Differentiate between string filepath (ex: from jsonify.GeographicRange) or list of filepaths.
        if type(json_files) == str:
            self.json_files = [idx for idx in json_files.split(" ")]
        elif type(json_files) == list:
            self.json_files = json_files

        # Other variables.
        self.names = [os.path.basename(self.json_files[idx]).rsplit(".json")[0] for idx in range(len(self.json_files))]
        self.data = [gpd.read_file(self.json_files[idx]) for idx in range(len(self.json_files))]

    
    def plot_two_polygons_intersection(self, figsize = (12, 9), alpha = 0.5):
        """
        Plot the intersection of two polygons built from latitue/longitude occurrence data.
        Expects a list of exactly two GeoJSON files.
        """
        
        # Get geographic ranges.
        gdf_0 = self.data[0][(self.data[0]["type"] == "geographic_range")]
        gdf_1 = self.data[1][(self.data[1]["type"] == "geographic_range")]

        # Get intersection by overlaying dataframes.
        isn = gpd.tools.overlay(gdf_0, gdf_1, 'intersection')

        # Add axis and basemap, converting tilemap from Web Mercator to WGS84.
        ax = isn.plot(figsize = figsize, alpha = alpha)
        cx.add_basemap(
            ax,
            crs = gdf_0.crs.to_string(),
            source = cx.providers.OpenStreetMap.Mapnik
        )


    def plot_many_polygons(self, figsize = (12, 9), alpha = 0.5):
        """
        Input a list of GeoJSON files and generate a static polygon map
        from each.
        """

        # Set up figures and axis.
        f, axs = plt.subplots(nrows = len(self.json_files), figsize = figsize)

        # Iterate over list of GeoJSON files.
        for idx in range(len(self.json_files)):

            # Get geographic range.
            gdf = self.data[idx][(self.data[idx]["type"] == "geographic_range")]

            # Plot range on unique axis.
            gdf.plot(ax = axs[idx], figsize = figsize, alpha = alpha)

            # Add basemap, converting tilemap from Web Mercator to WGS84.
            cx.add_basemap(
                axs[idx],
                crs = gdf.crs.to_string(),
                source = cx.providers.OpenStreetMap.Mapnik
            )