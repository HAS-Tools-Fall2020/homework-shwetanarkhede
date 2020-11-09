# %% 
# HW 11 
# Team SARS
# 11/8/2020

# %%
# Load Python Libraries
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np
import geopandas as gpd
import fiona
from shapely.geometry import Point
import contextily as ctx


# %%
# Dataset 1:  gage locations
# Gauges II USGS stream gauge dataset: https://water.usgs.gov/GIS/metadata/usgswrd/XML/gagesII_Sept2011.xml#stdorder
# Reading it using geopandas
file = os.path.join('E://datasets//gagesII_9322_sept30_2011.shp')
gages = gpd.read_file(file)

# Arizona gages
gages_az=gages[gages['STATE']=='AZ']

# Isolate verde river gage (via station ID) and project onto gages map
verde_stid = gages_az[gages_az['STAID'] == '09506000']
verde_gage = verde_stid.to_crs(gages_az.crs)


# %% 
# Dataset 2:  watershed boundaries
# Watersheds dataset:  https://www.usgs.gov/core-science-systems/ngp/national-hydrography/access-national-hydrography-products
# Watershed boundaries for the lower colorado 
file = os.path.join('E://datasets//WBD_15_HU2_GDB.gdb')
HUC6 = gpd.read_file(file, layer="WBDHU6")

# Project lower colorado watersheds onto gages map
HUC6_project = HUC6.to_crs(gages_az.crs)

# Isolate verde river watershed boundary and project onto gages map
HUC6_verde = HUC6[HUC6['name'] == 'Verde']
HUC6_verde_project = HUC6_verde.to_crs(gages_az.crs)


# %%
# Dataset 3:  rivers
# Rivers dataset:  https://repository.arizona.edu/handle/10150/188710
file = os.path.join('E://datasets//az_hydro_routesNAD83.shp')
fiona.listlayers(file)

# Define Arizona rivers and project onto gages map
az_rivers = gpd.read_file(file)
az_proj_rivers = az_rivers.to_crs(gages.crs)

# Isolate verde river and project onto gages map
river_verde = az_rivers[az_rivers['NAME'] == 'Verde River']
river_verde_project = river_Verde.to_crs(gages_az.crs)


# %%
# Function: plot variables and data onto a single map
def plot_map(dcolumn='DRAIN_SQKM', categorical=False,
              legend=True, markersize=45, cmap='RdBu',
              ax=ax):   
    fig, ax = plt.subplots(figsize=(10, 10))       

    # Zoom in plot to focus on verde river
    xlim = ([-1600000, -1300000])
    ylim = ([1250000, 1600000])
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    # Data points and layers (inc. basemap)
    gages_az.plot(ax=ax, label='Stream Gages', color='darkgreen', edgecolor='white', markersize=50, zorder=5)
    HUC6_project.boundary.plot(ax=ax, label='HUC6 Boundary', color=None, edgecolor='black', linewidth=1, zorder=1, alpha=0.5)
    HUC6_verde_project.boundary.plot(ax=ax, label='Verde Watershed', color=None, edgecolor='black', linewidth=2, zorder=2)
    az_proj_rivers.plot(ax=ax, label='Rivers', color='blue', zorder=3, alpha=0.4)
    river_verde_project.plot(ax=ax, label='Verde River', linewidth=2, color='blue', zorder=4)
    verde_gage.plot(ax=ax, label='Verde River Gage', color='red', edgecolor='white', marker='v', markersize=250, zorder=6)
    ctx.add_basemap(ax, crs=gages_az.crs, url=ctx.providers.OpenTopoMap, zorder=0, alpha=0.5)

    # Plot axis/data titles
    ax.set_title('Verde River Stream Gage', fontsize=20)
    ax.set_xlabel('Easting (m)')
    ax.set_ylabel('Northing (m)')
    ax.legend()  
    return fig, ax
  
  
# %%
# Run function to plot data and save as image
fig, ax = plot_map(gages_az)  
fig.savefig(f'map_verde.png', bbox_inches = 'tight')


# %%
