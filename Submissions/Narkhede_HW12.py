# Autoregressive Model for forecasting weekly streamflow upto 16 weeks
# Reading NetCDF4 files
# Editor: Shweta Narkhede
# Last edited: Nov 15th, 2020

# %%
# Importing required packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import urllib.request as req
import urllib
import model_function as mf
from sklearn.linear_model import LinearRegression
import xarray as xr
import rioxarray
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import seaborn as sns
import geopandas as gpd
import fiona
import shapely
from netCDF4 import Dataset
import model_function as mf

# %%
# Collecting datasets:
# 1. Streamflow data from USGS website
# 2. Precipitation from NOAA website (https://psl.noaa.gov/cgi-bin/db_search/SearchMenus.pl) NetCDF4 files
# 3. Air temperature from NOAA website (https://psl.noaa.gov/cgi-bin/db_search/SearchMenus.pl) NetCDF4 files

# Getting streamflow data

site = '09506000'
start = "2019-01-01"
end = "2020-11-11"

url = "https://waterdata.usgs.gov/nwis/dv?cb_00060=on&format=rdb&site_no=" \
      + site + "&referred_module=sw&period=&begin_date=" + start + \
      "&end_date=" + end
# $ Only works if you select tab seperated data
flowdata = pd.read_table(url, sep='\t', skiprows=30,
                         names=['agency_cd', 'site_no',
                                'datetime', 'flow', 'code'],
                         parse_dates=['datetime'])

# Expanding the dates to year, month, day and day of week
flowdata['year'] = pd.DatetimeIndex(flowdata['datetime']).year
flowdata['month'] = pd.DatetimeIndex(flowdata['datetime']).month
flowdata['day'] = pd.DatetimeIndex(flowdata['datetime']).day
flowdata['dayofweek'] = pd.DatetimeIndex(flowdata['datetime']).dayofweek

# Aggregating flow values to weekly (weekly averaged flow)
flow_weekly = flowdata.resample("W", on='datetime').mean()

# %%
# Getting precipitation data (Net CDF file historical time series)
# https://towardsdatascience.com/handling-netcdf-files-using-xarray-for-absolute-beginners-111a8ab4463f
data_path = os.path.join('../data',
                         'Reanalysis_Precipitation.nc')
os.path.exists(data_path)
# Read in the dataset as an x-array
dataset = xr.open_dataset(data_path)

# We can inspect the metadata of the file like this:
metadata = dataset.attrs
metadata
# And we can grab out any part of it like this:
metadata['dataset_title']

# we can also look at other  attributes like this
dataset.values
dataset.dims
dataset.coords

# Focusing on just the precip values
precip = dataset['prate']
precip

# Now to grab out data first lets look at spatail coordinates:
dataset['prate']['lat'].values.shape
# The first 4 lat values
dataset['prate']['lat'].values
dataset['prate']['lon'].values

# Now looking at the time;
dataset["prate"]["time"].values
dataset["prate"]["time"].values.shape


# Now lets take a slice: Grabbing data for just one point
lat = dataset["prate"]["lat"].values[0]
lon = dataset["prate"]["lon"].values[0]
print("Long, Lat values:", lon, lat)
one_point = dataset["prate"].sel(lat=lat, lon=lon)
one_point.shape

# Verde gage station [-111.789871, 34.448361]

# Convert to dataframe
precipdata = one_point.to_dataframe()

# Convert to weekly dataset
precip_weekly = precipdata.resample("W", axis=0).mean()

# Pulling required (only 2020) dataset to use in AR model
# precip_input = precip_weekly.loc['2020-01-01':'2020-11-11']

# %% Getting Air temperature data from NetCDF file
data_path = os.path.join('../data',
                         'Reanalysis_Air_temp.nc')
os.path.exists(data_path)
dataset2 = xr.open_dataset(data_path)
metadata2 = dataset2.attrs

# Focusing on just the air temperature values
airtemp = dataset2['air']

# Now to grab out data first lets look at spatial coordinates:
dataset2['air']['lat'].values.shape
# The first 4 lat values
dataset2['air']['lat'].values
dataset2['air']['lon'].values

# Now looking at the time;
dataset2["air"]["time"].values
dataset2["air"]["time"].values.shape


# Now lets take a slice: Grabbing data for just one point
lat = dataset2["air"]["lat"].values[0]
lon = dataset2["air"]["lon"].values[0]
print("Long, Lat values:", lon, lat)
one_point2 = dataset2["air"].sel(lat=lat, lon=lon)
one_point2.shape

# Verde gage station [-111.789871, 34.448361]

# Convert to dataframe
airtempdata = one_point2.to_dataframe()

temp_weekly = airtempdata.resample("W", axis=0).mean()

# Converting temperature units to imperial system
temp_weekly['air'] = (temp_weekly.air-273.15)*9/5 + 32

# Pulling required (only 2020) dataset to use in AR model
#temp_input = temp_weekly.loc['2020-01-01':'2020-11-11']
# %%
# Combining data in single dataframe to use for AR model
Comb_data = flow_weekly
Comb_data['Precip'] = precip_weekly.prate.values
Comb_data['Air_temp'] = temp_weekly.air.values

# %%
# Adding lagged streamflow dataset to dataframe for AR model

for i in range(1, 9):
    Comb_data['tm' '%s' % (i)] = flow_weekly['flow'].shift(i)


mydata = Comb_data[(Comb_data['year'] >= 2020) &
                   (Comb_data['month'] <= 10) &
                   (Comb_data['month'] >= 8)][['flow', 'tm1', 'tm2',
                                               'tm3', 'tm4', 'tm5', 'tm6',
                                               'tm7', 'tm8', 'Precip', 'Air_temp']]


# %%
# Forecast using AR Model

predicted_flows = pd.DataFrame(columns=["Week", "Flow"])
current_week = 12
inputs = ['tm1', 'tm2', 'tm3', 'tm4', 'tm5',
          'tm6', 'tm7', 'tm8', 'Precip', 'Air_temp']
# For loop for making predictions for 16 weeks
# For loop for making predictions for 16 weeks
for i in range(current_week, 16):
    x1 = mydata[inputs].values
    y1 = mydata[['flow']].values
    last_week_flow = mydata.tail(1)[inputs]
    nextweek_pred = mf.AR_Model(x1, y1, last_week_flow).round(2)

    mydata = mydata.append({'flow': nextweek_pred,
                            'tm1': mydata.flow[(mydata.flow.size-1)],
                            'tm2': mydata.flow[(mydata.flow.size-2)],
                            'tm3': mydata.flow[(mydata.flow.size-3)],
                            'tm4': mydata.flow[(mydata.flow.size-4)],
                            'tm5': mydata.flow[(mydata.flow.size-5)],
                            'tm6': mydata.flow[(mydata.flow.size-6)],
                            'tm7': mydata.flow[(mydata.flow.size-7)],
                            'tm8': mydata.flow[(mydata.flow.size-8)],
                            'Precip': mydata.Precip.tail(2).mean(),
                            'Air_temp': mydata.Air_temp.tail(2).mean()
                            }, ignore_index=True)
    # Adding correction factor of 80 cfs
    predicted_flows = predicted_flows.append(
        {'Week': [i+1], 'Flow': nextweek_pred + 80}, ignore_index=True)

print(predicted_flows)
# Forecast entries for previous weeks (Week 1 to 10)
previous_weeks_entries = pd.Series(flow_weekly.flow.tail(current_week).values)

# Total 16 weeks entries to be submitted for forecast competition
Forecast_entries = pd.DataFrame(columns=["Week", "Flow"])
aggregate = previous_weeks_entries.append(predicted_flows.Flow)
Forecast_entries['Flow'] = aggregate.T
Forecast_entries['Week'] = range(1, 17)
Forecast_entries = Forecast_entries.set_index('Week')
print(Forecast_entries)
print('Week 1 forecast = ', Forecast_entries.Flow[current_week+1],
      ' and Week 2 Forecast = ', Forecast_entries.Flow[current_week+2])

# %%

# PLOTTING DATA

# Precipitation
f, ax = plt.subplots(figsize=(8, 5))
one_point.plot.line(hue='lat',
                    marker="X",
                    ax=ax,
                    color="grey",
                    markerfacecolor="g",
                    markeredgecolor="g",
                    markersize=6)
ax.set(title="Daily average precipitation rate time series")
f.savefig("Precipitation rate.png")

# Air temperature
f, ax = plt.subplots(figsize=(8, 5))
one_point2.plot.line(hue='lat',
                     marker="s",
                     ax=ax,
                     color="grey",
                     markerfacecolor="Red",
                     markeredgecolor="Red",
                     markersize=3)
ax.set(title="Air temperature daily average time series")
f.savefig("Air temperature.png")

# %%
