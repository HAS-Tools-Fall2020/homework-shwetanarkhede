# Homework Assignment # 11 (Week 11)
# Modified by : SARS
# Last modified on: Nov 7th, 2020


# %%
import numpy as np
import pandas as pd
import json
import urllib.request as req
import urllib
import model_function as mf
import plot_function as plotf
from sklearn.linear_model import LinearRegression

# %%
site = '09506000'
start = "2000-10-08"
end = "2020-10-24"

url = "https://waterdata.usgs.gov/nwis/dv?cb_00060=on&format=rdb&site_no=" \
      + site + "&referred_module=sw&period=&begin_date=" + start + \
      "&end_date=" + end
# $ Only works if you select tab seperated data
data2 = pd.read_table(url, sep='\t', skiprows=30,
                      names=['agency_cd', 'site_no',
                             'datetime', 'flow', 'code'],
                      parse_dates=['datetime'])

# Expanding the dates to year, month, day and day of week
data2['year'] = pd.DatetimeIndex(data2['datetime']).year
data2['month'] = pd.DatetimeIndex(data2['datetime']).month
data2['day'] = pd.DatetimeIndex(data2['datetime']).day
data2['dayofweek'] = pd.DatetimeIndex(data2['datetime']).dayofweek

# Aggregating flow values to weekly (weekly averaged flow)
flow_weekly = data2.resample("W", on='datetime').mean()

# Combining both time series in single dataframe
Comb_data = flow_weekly

# %%
for i in range(1, 9):
    flow_weekly['tm' '%s' % (i)] = flow_weekly['flow'].shift(i)

lag_cols = ['tm1', 'tm2', 'tm3', 'tm4', 'tm5', 'tm6', 'tm7', 'tm8']
# Step 2: Selecting data to use for prediction
# LC - It looks like you are grabbing out all the rows of data so you could
#  skip the part on line 59?
mydata = Comb_data[(Comb_data['year'] >= 2019) &
                   (Comb_data['month'] <= 10) &
                   (Comb_data['month'] >= 8)][['flow', 'tm1', 'tm2',
                                               'tm3', 'tm4', 'tm5', 'tm6',
                                               'tm7', 'tm8']]

# %%
# Using AR_model function to predict streamflows for 16 weeks
# Creating empty dataframe for storing predicted flows
predicted_flows = pd.DataFrame(columns=["Week", "Flow"])

# For loop for making predictions for 16 weeks
for i in range(16):
    x1 = mydata[lag_cols].values
    y1 = mydata[['flow']].values
    last_week_flow = mydata.tail(1)[lag_cols]
    nextweek_pred = mf.AR_Model(x1, y1, last_week_flow).round(2)

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

    predicted_flows = predicted_flows.append(
        {'Week': [i+1], 'Flow': nextweek_pred}, ignore_index=True)

print(predicted_flows)

# %%
# Plotting section:
# Previous steps: creating some additional dataset to plot.
# Calculating the historical daily mean without 2020

hist_flow = plotf.hist_daily_mean(data2, 2020)

# Calculating the weekly mean
week_hist = plotf.weekly_mean(hist_flow, 8, 22, 16)
week_2019 = plotf.weekly_mean(data2, 8, 22, 16, 2019)

# From the forecast dataframe
week_forecast = predicted_flows['Flow'].T

# Finally, plotting

plotf.plot_3series(week_hist, week_2019, week_forecast, 2019)

# %%
