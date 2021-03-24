#!/usr/bin/env python

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.cm as cm
import seaborn as sns
from shapely.geometry import Polygon
import matplotlib.patches as mpatches
import numpy as np
import math
import libpysal


# TODO: why do the above things appear as options in tab completion?


# Make dataframes have wider columns for neatness.
pd.set_option("max_colwidth", 14)


# TODO: Filtering outlier points matters for both polygons and plotting.  One option is calculating distance from
# a centroid.  That means making a polygon, removing points too far away from the array, then making the polygon again.
def centroid(data):
    """
    calculate centroid of occurrence points

    data must be a dataframe with 'Latitude' and 'Longitude' columns
    """
    x = 0.0
    y = 0.0
    z = 0.0

    for i, coord in data.iterrows():
        latitude = math.radians(coord.Latitude)
        longitude = math.radians(coord.Longitude)

        x += math.cos(latitude) * math.cos(longitude)
        y += math.cos(latitude) * math.sin(longitude)
        z += math.sin(latitude)

    total = len(data)

    x = x / total
    y = y / total
    z = z / total

    central_longitude = math.atan2(y, x)
    central_square_root = math.sqrt(x * x + y * y)
    central_latitude = math.atan2(z, central_square_root)

    mean_location = {
        'latitude': math.degrees(central_latitude),
        'longitude': math.degrees(central_longitude)
        }

    return mean_location


def hexmap(data, figsize = (12, 9), gridsize = 10, alpha = 0.5, cmap = 'viridis_r'):
    """
    Build a hex-based grid map from arrays of latitude/longitude occurrence data.
    The gridsize parameter controls the size of the hexaognal "bins" of point data.
    """

    # Build a GeoDataFrame with geometry object from CSV file of lat/lon data, in WGS84 system.
    df = pd.read_csv(data)
    gdf = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df.Longitude, df.Latitude), crs = 'EPSG:4326')

    # Set GeoDataFrame to follow WGS84 system.
    # gdf.set_crs(epsg = 4326, inplace = True)

    # Set up figure and axis.
    f, ax = plt.subplots(1, figsize = figsize)

    # Generate and add hexbins, no borderlines, half transparency.
    ax.hexbin(
        gdf["Longitude"], # x
        gdf["Latitude"], # y
        gridsize = gridsize,
        linewidths = 0,
        alpha = alpha,
        cmap = cmap
    )

    # Add basemap, converting tilemap in Web Mercator to WGS84.
    cx.add_basemap(
       ax,
       crs = gdf.crs.to_string(),
       source = cx.providers.OpenStreetMap.Mapnik
    )

    # Add colorbar, forcing it to match figure size.
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    plt.colorbar(cm.ScalarMappable(norm = None, cmap = cmap), ax = ax, cax = cax)

    # Remove axes.
    ax.set_axis_off()
    

def recmap(data, figsize = (12, 9), bins = 10, cmin = None, cmax = None, alpha = 0.5, cmap = 'viridis_r'):
    """
    Build a rectangle-based grid map from latitude/longitude occurrence data.
    Bins can be specified as a single integer to produce equal bins in two
    dimensions (a square), or a list of two integers [int, int]
    to create rectangular binning.
    """

    # Build a GeoDataFrame with geometry object from CSV file of lat/lon data, in WGS84 system.
    df = pd.read_csv(data)
    gdf = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df.Longitude, df.Latitude), crs = 'EPSG:4326')

    # Set GeoDataFrame to follow WGS84 system.
    # gdf.set_crs(epsg = 4326, inplace = True)

    # Set up figure and axis.
    f, ax = plt.subplots(1, figsize = figsize)

    # Generate and add 2D histogram.
    ax.hist2d(
        gdf["Longitude"], # x
        gdf["Latitude"], # y
        bins = bins,
        cmin = cmin,
        cmax = cmax,
        alpha = alpha,
        cmap = cmap,
    )

    # Add basemap, converting tilemap in Web Mercator to WGS84.
    cx.add_basemap(
       ax,
       crs = gdf.crs.to_string(),
       source = cx.providers.OpenStreetMap.Mapnik
    )

    # Add colorbar, forcing it to match figure size.
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    plt.colorbar(cm.ScalarMappable(norm = None, cmap = cmap), ax = ax, cax = cax)

    # Remove axes.
    ax.set_axis_off()


def kdemap(data, figsize = (12, 9), levels = 50, alpha = 0.5, cmap = 'viridis_r'):
    """
    Build a map of kernel density estimation from latitude/longitude occurrence data.  
    levels controls the degree of gradient shading.
    """

    # Build a GeoDataFrame with geometry object from CSV file of lat/lon data, in WGS84 system.
    df = pd.read_csv(data)
    gdf = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df.Longitude, df.Latitude), crs = 'EPSG:4326')

    # Set GeoDataFrame to follow WGS84 system.
    # gdf.set_crs(epsg = 4326, inplace = True)

    # Set up figure and axis
    f, ax = plt.subplots(1, figsize = figsize)

    # Generate and add KDE with a shading of 50 gradients, colored contours, 75% transparency, and the reverse viridis colormap.
    sns.kdeplot(
        gdf["Longitude"], # x
        gdf["Latitude"], # y
        n_levels = levels,
        shade = True,
        alpha = alpha,
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


def plot_polygons_intersection(data1, data2, figsize = (12, 9), alpha = 0.5):
    '''
    Plot the intersection of two polygons built from latitue/longitude occurrence data.
    '''

    # Load data.
    df1 = pd.read_csv(data1)
    df2 = pd.read_csv(data2)

    # Build dicts, including convex hull polygons.
    d1 = {'name': ['name1'], 'geometry': [Polygon(gpd.points_from_xy(df1.Longitude, df1.Latitude)).convex_hull]}
    d2 = {'name': ['name2'], 'geometry': [Polygon(gpd.points_from_xy(df2.Longitude, df2.Latitude)).convex_hull]}

    # Build GeoDataFrames in WGS84 system.
    g1 = gpd.GeoDataFrame(d1, crs = 'EPSG:4326')
    g2 = gpd.GeoDataFrame(d2, crs = 'EPSG:4326')

    # geopandas calculates intersections by overlapping at the dataframe level.
    # TODO: is a direct intersection the best measure of overlap? Review lit.
    # TODO: can I get the perimeter of this intersection?
    isn = gpd.tools.overlay(g1, g2, 'intersection')

    # Plot the intersection.
    ax = isn.plot(figsize = figsize, alpha = alpha)
    cx.add_basemap(
        ax,
        crs = g1.crs.to_string(),
        source = cx.providers.OpenStreetMap.Mapnik
    )


def plot_polygons_separate(
    data1,
    data2,
    label1 = None,
    label2 = None,
    sep = False,
    legend = False,
    figsize = (30, 30),
    alpha = 0.5,
    fontsize = 20,
    markerscale = 10):
    '''
    Plot two polygons built from latitude/longitude occurrence data,
    either separately on two figures, or overlaid on one figure.
    '''

    # Load data.
    df1 = pd.read_csv(data1)
    df2 = pd.read_csv(data2)

    # Build convex hull polygons.
    poly1 = Polygon(gpd.points_from_xy(df1.Longitude, df1.Latitude)).convex_hull
    poly2 = Polygon(gpd.points_from_xy(df2.Longitude, df2.Latitude)).convex_hull

    # Build two GeoSeries in WGS84 system.
    p1 = gpd.GeoSeries(poly1, crs = 'EPSG:4326')
    p2 = gpd.GeoSeries(poly2, crs = 'EPSG:4326')

    # By default, plot the two polygons on top of each other.
    if not sep:
        f, ax = plt.subplots(ncols = 1, figsize = figsize)
        p1.plot(ax = ax, alpha = alpha, color = 'red', label = label1)
        p2.plot(ax = ax, alpha = alpha, color = 'blue', label = label2)
        if legend:
            l1 = mpatches.Patch(color = 'red', label = label1)
            l2 = mpatches.Patch(color = 'blue', label = label2)
            plt.legend(
                handles = [l1, l2], 
                loc = 'lower right', 
                bbox_to_anchor = (1, -0.25), 
                fontsize = fontsize, 
                markerscale = markerscale
                )

        # Add basemap, converting tilemap in Web Mercator to WGS84.
        cx.add_basemap(
            ax,
            crs = p1.crs.to_string(),
            source = cx.providers.OpenStreetMap.Mapnik
        )

    # Alternatively, plot each polygon on its own figure.
    else:
        f, (ax1, ax2) = plt.subplots(ncols = 2, sharex = True, sharey = True, figsize = figsize)
        p1.plot(ax = ax1, alpha = alpha, color = 'red', label = label1)
        p2.plot(ax = ax2, alpha = alpha, color = 'blue', label = label2)
        if legend:
            l1 = mpatches.Patch(color = 'red', label = label1)
            l2 = mpatches.Patch(color = 'blue', label = label2)
            plt.legend(
                handles = [l1, l2],
                loc = 'lower center',
                bbox_to_anchor = (-0.15, -0.5),
                fontsize = fontsize,
                markerscale = markerscale
                )

        # Add a basemap to each figure.
        cx.add_basemap(
            ax1,
            crs = p1.crs.to_string(),
            source = cx.providers.OpenStreetMap.Mapnik
        )
        cx.add_basemap(
            ax2,
            crs = p2.crs.to_string(),
            source = cx.providers.OpenStreetMap.Mapnik
        )


def get_cartesian(lats, lons):
    """
    Transform latitude and longitude coordinates into (roughly) Cartesian equivalents.
    """

    # Create three empty arrays.
    cart_y = np.zeros((len(lats), 1))
    cart_x = np.zeros((len(lats), 1))
    cart_z = np.zeros((len(lats), 1))

    # Set R, the approximate radius of the Earth in kilometers.
    R = 6371

    # Calculate XYZ coordinates.
    for idx in range(len(lats)):
        Y = R * math.cos(lats[idx]) * math.sin(lons[idx])
        X = R * math.cos(lats[idx]) * math.cos(lons[idx])
        Z = R * math.sin(lats[idx])
        cart_y[idx] = Y
        cart_x[idx] = X
        cart_z[idx] = Z

    # Return XY coordinates.
    return cart_y, cart_x, cart_z
     

def calculate_overlay(lats1, lons1, lats2, lons2):
    """
    Calculate the intersection of two polygons constructed as alpha shapes from
    latitude/longitude occurrence data of two taxa.
    """

    # Transform to arrays of Cartesian coordinates.
    cart_y1, cart_x1, cart_z1 = get_cartesian(lats1, lons1)
    cart_y2, cart_x2, cart_z2 = get_cartesian(lats2, lons2)

    # Create XY lists and XYZ lists.
    coords1 = np.append(cart_x1, cart_y1, axis = 1)
    coords1z = np.append(coordinates1, cart_z1, axis = 1)
    coords2 = np.append(cart_x2, cart_y2, axis = 1)
    coords2z = np.append(coordinates2, cart_z2, axis = 1)

    # Calculate alpha shapes from XY lists.
    alpha_shape1, alpha1, circs1 = libpysal.cg.alpha_shape_auto(coordinates1, return_circles = True)
    alpha_shape2, alpha2, circs2 = libpysal.cg.alpha_shape_auto(coordinates2, return_circles = True)

    # Create two empty arrays, each the length of the total number of coordinates comprising the alpha shape.
    as1c = np.zeros((len(alpha_shape1.exterior.coords.xy[0]), 2))
    as2c = np.zeros((len(alpha_shape2.exterior.coords.xy[0]), 2))

    # Fill the arrays with the rearranged alpha shape coordinates.
    for i in range(len(as1c)):
        as1c[i][0] = alpha_shape1.exterior.coords.xy[0][i] # alpha_shape1 x
        as1c[i][1] = alpha_shape1.exterior.coords.xy[1][i] # alpha_shape1 y
    for i in range(len(as2c)):
        as2c[i][0] = alpha_shape2.exterior.coords.xy[0][i] # alpha_shape2 x
        as2c[i][1] = alpha_shape2.exterior.coords.xy[1][i] # alpha_shape2 y

    # TODO: compare as1c and as2c to XYZ lists to find coords to convert back to lat/lon.  The polygon of those points
    # would be desired for intersection.

    # Build two GeoDataFrames for the final shapes.
    # d1 = {'name': ['name1'], 'geometry': [alpha_shape1]}
    # d2 = {'name': ['name2'], 'geometry': [alpha_shape2]}
    # g1 = gpd.GeoDataFrame(d1)
    # g2 = gpd.GeoDataFrame(d2)

    # Calculate and plot the intersection. 
    # isn = gpd.tools.overlay(g1, g2, 'intersection')
    # isn.plot()


def world_plot(
    data1,
    data2 = None,
    label1 = None,
    label2 = None,
    legend = False,
    figsize = (15, 15),
    fontsize = 20,
    markerscale = 10):
    '''
    Plot worldwide occurrence data for one or two taxa.
    '''

    # Get world map from geopandas.
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    world = world[(world.pop_est > 0) & (world.name != "Antarctica")]
    base = world.plot(color = 'white', edgecolor = 'black', figsize = figsize)

    # Plot first set of occurrence data.
    df1 = pd.read_csv(data1)
    gdf1 = gpd.GeoDataFrame(df1, geometry = gpd.points_from_xy(df1.Longitude, df1.Latitude), crs = world.crs)
    gdf1.plot(ax = base, marker = 'o', color = 'red', markersize = 5, label = label1)

    # If there is a second set of occurrence data, plot that as well.
    if data2:
        df2 = pd.read_csv(data2)
        gdf2 = gpd.GeoDataFrame(df2, geometry = gpd.points_from_xy(df2.Longitude, df2.Latitude), crs = world.crs)
        gdf2.plot(ax = base, marker = 'o', color = 'blue', markersize = 5, label = label2)

    # Add legend.
    if legend:
        base.legend(loc = 'lower right', bbox_to_anchor = (1, -0.25), fontsize = fontsize, markerscale = markerscale);