# 599 HAS tools Homeowrk Assignment # 15 (Week 15)
# Author: Shweta Narkhede
# LAst Modified on: Dec 6th, 2020

# Python Code of Autoregressive model for forecasting weekly averaged streamflow for 16 weeks

# %%
# Importing required packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import urllib

from sklearn.linear_model import LinearRegression
# %%


def AR_Model(x, y, last_week_flow):
    """ fucntion for AR model

    Parameters
    ----------
    input : arrays and dataframes
    x & y are arrays of training datasets while last_week_flow is
    the dataframe of latest flow record.

    Returns
    ------
    output : array
    Output is a flow value of week1 prediction in cfs
    """
    # Fitting AR model to training dataset
    model = LinearRegression().fit(x, y)

    # Printing model fitting parameters
    r_sq1 = model.score(x, y)
    # print('Coefficient of Determination = ', np.round(r_sq1, 2))

    # Predicting flows with fitted AR Model
    nextweek_prediction = model.predict(last_week_flow)

    # Output of this function will be printed as forecasted streamflow
    return nextweek_prediction
# %%
# Collecting datasets:
# 1. Streamflow data from USGS website
# 2. Precipitation from NOAA website (https://psl.noaa.gov/cgi-bin/db_search/SearchMenus.pl) NetCDF4 files
# 3. Air temperature from NOAA website (https://psl.noaa.gov/cgi-bin/db_search/SearchMenus.pl) NetCDF4 files

# Getting streamflow data


site = '09506000'
start = "1989-01-01"
end = "2020-21-08"

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
# Combining data in single dataframe to use for AR model
Comb_data = flow_weekly

# %%
# Adding lagged streamflow dataset to dataframe for AR model

for i in range(1, 9):
    Comb_data['tm' '%s' % (i)] = flow_weekly['flow'].shift(i)


mydata = Comb_data[(Comb_data['year'] >= 2019) &
                   (Comb_data['month'] <= 10) &
                   (Comb_data['month'] >= 8)][['flow', 'tm1', 'tm2',
                                               'tm3', 'tm4', 'tm5', 'tm6',
                                               'tm7', 'tm8']]


# %%
# Forecast using AR Model

predicted_flows = pd.DataFrame(columns=["Week", "Flow"])
current_week = 0
inputs = ['tm1', 'tm2', 'tm3', 'tm4', 'tm5',
          'tm6', 'tm7', 'tm8']
# For loop for making predictions for 16 weeks
# For loop for making predictions for 16 weeks
for i in range(current_week, 16):
    x1 = mydata[inputs].values
    y1 = mydata[['flow']].values
    last_week_flow = mydata.tail(1)[inputs]
    nextweek_pred = AR_Model(x1, y1, last_week_flow).round(2)

    mydata = mydata.append({'flow': nextweek_pred,
                            'tm1': mydata.flow[(mydata.flow.size-1)],
                            'tm2': mydata.flow[(mydata.flow.size-2)],
                            'tm3': mydata.flow[(mydata.flow.size-3)],
                            'tm4': mydata.flow[(mydata.flow.size-4)],
                            'tm5': mydata.flow[(mydata.flow.size-5)],
                            'tm6': mydata.flow[(mydata.flow.size-6)],
                            'tm7': mydata.flow[(mydata.flow.size-7)],
                            'tm8': mydata.flow[(mydata.flow.size-8)]
                            }, ignore_index=True)
    # Adding correction factor of 80 cfs
    predicted_flows = predicted_flows.append(
        {'Week': [i], 'Flow': nextweek_pred+20}, ignore_index=True)

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
print('Week 1 forecast = ', Forecast_entries.Flow[current_week+1][0][0],
      ' and Week 2 Forecast = ', Forecast_entries.Flow[current_week+2][0][0])

Forecast_entries.to_csv(
    '../Submissions/Week_15_forecast.xls', index=False)
