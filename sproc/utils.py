#!/usr/bin/env python

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import contextily as cx
import seaborn as sns
import math
import libpysal


def hexmap(data, figsize = (12, 9), gridsize = 10, cmap = 'viridis_r'):
    """
    Build a hex-based grid map from arrays of latitude/longitude occurrence data.  The gridsize parameter controls
    the size of the hexaognal "bins" of point data.
    """

    # Build a GeoDataFrame with geometry object from CSV file of lat/lon data.
    df = pd.read_csv(data)
    gdf = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df.Longitude, df.Latitude))

    # Set GeoDataFrame to follow WGS84 system.
    gdf.set_crs(epsg = 4326, inplace = True)

    # Set up figure and axis.
    f, ax = plt.subplots(1, figsize = figsize)

    # Generate and add hexbins, no borderlines, half transparency.
    hb = ax.hexbin(
        gdf["Longitude"], # x
        gdf["Latitude"], # y
        gridsize = gridsize,
        linewidths = 0,
        alpha = 0.5, 
        cmap = cmap
    )

    # Add basemap, converting tilemap in Web Mercator to WGS84.
    cx.add_basemap(
       ax, 
       crs = gdf.crs.to_string(),
       source = cx.providers.OpenStreetMap.Mapnik
    )

    # Add colorbar.  plt.colorbar(hb) also works fine, but this is more direct?
    plt.colorbar(cm.ScalarMappable(norm = None, cmap = cmap), ax = ax)

    # Remove axes.
    ax.set_axis_off()
    

def recmap(data, figsize = (12, 9), bins = 10, cmin = None, cmax = None, cmap = 'viridis_r'):
    """
    Build a rectangle-based grid map from latitude/longitude occurrence data.  Bins can be specified as
    a single integer to produce equal bins in two dimensions (a square), or a list of two integers [int, int]
    to create rectangular binning.
    """

    # Build a GeoDataFrame with geometry object from CSV file of lat/lon data.
    df = pd.read_csv(data)
    gdf = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df.Longitude, df.Latitude))

    # Set GeoDataFrame to follow WGS84 system.
    gdf.set_crs(epsg = 4326, inplace = True)

    # Set up figure and axis.
    f, ax = plt.subplots(1, figsize = figsize)

    # Generate and add 2D histogram.
    h2d = ax.hist2d(
        gdf["Longitude"], # x
        gdf["Latitude"], # y
        bins = bins,
        cmin = cmin,
        cmax = cmax,
        alpha = 0.5,
        cmap = cmap,
    )

    # Add basemap, converting tilemap in Web Mercator to WGS84.
    cx.add_basemap(
       ax, 
       crs = gdf.crs.to_string(),
       source = cx.providers.OpenStreetMap.Mapnik
    )

    # Add colorbar.
    plt.colorbar(cm.ScalarMappable(norm = None, cmap = cmap), ax = ax)

    # Remove axes.
    ax.set_axis_off()


def kdemap(data, figsize = (12, 9), levels = 50, cmap = 'viridis_r'):
    """
    Build a map of kernel density estimation from latitude/longitude occurrence data.  levels controls
    the degree of gradient shading.
    """

    # Build a GeoDataFrame with geometry object from CSV file of lat/lon data.
    df = pd.read_csv(data)
    gdf = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df.Longitude, df.Latitude))

    # Set GeoDataFrame to follow WGS84 system.
    gdf.set_crs(epsg = 4326, inplace = True)

    # Set up figure and axis
    f, ax = plt.subplots(1, figsize = figsize)

    # Generate and add KDE with a shading of 50 gradients 
    # coloured contours, 75% of transparency,
    # and the reverse viridis colormap
    sns.kdeplot(
        gdf["Longitude"], # x
        gdf["Latitude"], # y
        n_levels = levels, 
        shade = True,
        alpha = 0.55, 
        cmap = cmap
    )

    # Add basemap, converting tilemap in Web Mercator to WGS84.
    cx.add_basemap(
       ax, 
       crs = gdf.crs.to_string(),
       source = cx.providers.OpenStreetMap.Mapnik
    )

    # Remove axes.
    ax.set_axis_off()


def get_cartesian(lats, lons):
    """
    Transform lattitude and longitude coordinates into (roughly) Cartesian equivalents.
    """

    # Create two empty arrays.
    cart_y = np.zeros((len(lats), 1))
    cart_x = np.zeros((len(lats), 1))

    # Set R, the approximate radius of the Earth in kilometers.
    R = 6371

    # Calculate XY coordinates.
    for idx in range(len(lats)):
        X = R * math.cos(lats[idx]) * math.cos(lons[idx])
        Y = R * math.cos(lats[idx]) * math.sin(lons[idx])
        cart_x[idx] = X
        cart_y[idx] = Y

    # Return XY coordinates.
    return cart_x, cart_y
        

def calculate_overlay(lats1, lons1, lats2, lons2):
    """
    Calculate the intersection of two polygons constructed as alpha shapes from 
    latitude/longitude occurrence data of two taxa.
    """

    # Transform to arrays of Cartesian coordinates.
    cart_y1, cart_x1 = get_cartesian(lats1, lons1)
    cart_y2, cart_x2 = get_cartesian(lats2, lons2)
    coordinates1 = np.append(cart_x1, cart_y1, axis = 1)
    coordinates2 = np.append(cart_x2, cart_y2, axis = 1)

    # Calculate alpha shapes.
    alpha_shape1, alpha1, circs1 = libpysal.cg.alpha_shape_auto(coordinates1, return_circles = True)
    alpha_shape2, alpha2, circs2 = libpysal.cg.alpha_shape_auto(coordinates2, return_circles = True)

    # TODO: is it possible to use geographic coordinates to build shape instead of Cartesian? 
    # If not, must transform back in order to plot in geographic coordinates.

    # Build two GeoDataFrames for the alpha shapes.
    d1 = {'name': ['name1'], 'geometry': [alpha_shape1]}
    d2 = {'name': ['name2'], 'geometry': [alpha_shape2]}
    g1 = gpd.GeoDataFrame(d1)
    g2 = gpd.GeoDataFrame(d2)

    # Calculate and plot the intersection.  TODO: is a direct intersection the best measure of overlap? Review lit.
    isn = gpd.tools.overlay(g1, g2, 'intersection')
    isn.plot()

