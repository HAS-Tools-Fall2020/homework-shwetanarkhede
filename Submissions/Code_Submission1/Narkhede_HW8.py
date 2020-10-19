# Autoregressive Model for forecasting weekly streamflow upto 16 weeks
# Author: Shweta Narkhede
# Last edited: Oct 18, 2020

# %%
# Importing the modules
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# %%
# Accessing data
filename = 'streamflow_week8.txt'
filepath = os.path.join('../../data', filename)
print(os.getcwd())
print(filepath)
os.path.exists(filepath)

# %%
# Reading data to Panadas dataframe
data = pd.read_table(filepath, sep='\t', skiprows=30,
                     names=['agency_cd', 'site_no',
                            'datetime', 'flow', 'code'],
                     parse_dates=['datetime'])

# Expanding the dates to year, month, day and day of week
data['year'] = pd.DatetimeIndex(data['datetime']).year
data['month'] = pd.DatetimeIndex(data['datetime']).month
data['day'] = pd.DatetimeIndex(data['datetime']).day
data['dayofweek'] = pd.DatetimeIndex(data['datetime']).dayofweek

# Aggregating flow values to weekly (weekly averaged flow)
flow_weekly = data.resample("W", on='datetime').mean()

# %%
# Building an Auto-regressive Model

# Step 1: Setting up the arrays based on lagged time series
# (upto 8 timestep lag)

for i in range(1, 9):
    flow_weekly[i] = flow_weekly['flow'].shift(i)
flow_weekly = flow_weekly.rename(columns={
    1: 'tm1', 2: 'tm2', 3: 'tm3', 4: 'tm4', 5: 'tm5',
    6: 'tm6', 7: 'tm7', 8: 'tm8'})

# Step 2: Selecting data to use for prediction
mydata = flow_weekly[(flow_weekly['year'] >= 2018) &
                     (flow_weekly['month'] <= 10) &
                     (flow_weekly['month'] >= 8)]
[['flow', 'tm1', 'tm2', 'tm3', 'tm4', 'tm5', 'tm6', 'tm7', 'tm8']]

# %%
# Creating function to use Auto-regressive model multiple times


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
    print('Coefficient of Determination = ', np.round(r_sq1, 2))

    # Predicting flows with fitted AR Model
    nextweek_prediction = model.predict(last_week_flow.values)

    # Output of this function will be printed as forecasted streamflow
    return nextweek_prediction

# %%
# Using AR_model function to predict streamflows for 16 weeks


# Creating empty dataframe for storing predicted flows
predicted_flows = pd.DataFrame(columns=["Week", "Flow"])

# For loop for making predictions for 16 weeks
for i in range(16):
    x1 = mydata[['tm1', 'tm2', 'tm3', 'tm4',
                 'tm5', 'tm6', 'tm7', 'tm8']].values
    y1 = mydata[['flow']].values
    last_week_flow = mydata.tail(1)[['tm1', 'tm2', 'tm3', 'tm4',
                                     'tm5', 'tm6', 'tm7', 'tm8']]
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

    predicted_flows = predicted_flows.append(
        {'Week': [i+1], 'Flow': nextweek_pred}, ignore_index=True)

print(predicted_flows)

# %%
# Plots

# Plot of weekly streamflows of selected data and predicted flows
# for next 16 weeks
fig, ax = plt.subplots()
ax.plot(range(1, 52), mydata.flow, 'g:', label='Observed flow')
ax.plot(range(36, 52),
        predicted_flows['Flow'], 'ro', label='Predicted flow')
ax.set(title="Sept & Oct weekly streamflows in 2019 - 2020",
       xlabel="Weeks", ylabel="Weekly Avg Flow [cfs]")
ax.legend()
fig.set_size_inches(12, 3)

# Plot of 16 weeks streamflow forecast
fig, ax = plt.subplots()
ax.plot(range(1, 17),
        predicted_flows['Flow'], 'ro--', label='Predicted flow')
ax.set(title="Streamflow forecast upto next 16 weeks",
       xlabel="Weeks", ylabel="Weekly Avg Flow [cfs]")
ax.legend()
fig.set_size_inches(12, 3)

# %%
