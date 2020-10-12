# Autoregressive Model for forecasting weekly streamflow
# Modified by: Shweta Narkhede
# Last edited: Oct 12, 2020. By Xenia.

# %%
# Importing the modules
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import datetime

# %%
# Accessing data
filename = 'streamflow_week7.txt'
filepath = os.path.join(r'C:\Users\xy_22\Documents\MSc._Hydrology\2020_Fall\599-HAS_Tools\homework-shwetanarkhede\Submissions\Code_Review1', filename)
print(os.getcwd())
print(filepath)


# %%
# Reading data to Panadas dataframe
data = pd.read_table(filepath, sep='\t', skiprows=30,
                     names=['agency_cd', 'site_no',
                            'datetime', 'flow', 'code'],
                     parse_dates=['datetime']
                     )

# Expanding the dates to year, month, day and day of week
data['year'] = pd.DatetimeIndex(data['datetime']).year
data['month'] = pd.DatetimeIndex(data['datetime']).month
data['day'] = pd.DatetimeIndex(data['datetime']).day
data['dayofweek'] = pd.DatetimeIndex(data['datetime']).dayofweek

# Aggregating flow values to weekly (weekly averaged flow)
flow_weekly = data.resample("W", on='datetime').mean()

# Enabling datetime index to easily check the flow on specific date
# flow_weekly.reset_index(level=None,drop=False, \
# inplace=True, \col_level=0, col_fill='')

# %%
# Building an Autoregressive Model

# Step 1: Setting up the arrays based on lagged time series
flow_weekly['flow_tm1'] = flow_weekly['flow'].shift(1)
flow_weekly['flow_tm2'] = flow_weekly['flow'].shift(2)
flow_weekly['flow_tm3'] = flow_weekly['flow'].shift(3)
flow_weekly['flow_tm4'] = flow_weekly['flow'].shift(4)
flow_weekly['flow_tm5'] = flow_weekly['flow'].shift(5)
flow_weekly['flow_tm6'] = flow_weekly['flow'].shift(6)
flow_weekly['flow_tm7'] = flow_weekly['flow'].shift(7)
flow_weekly['flow_tm8'] = flow_weekly['flow'].shift(8)

# Step 2: Selecting data to use for prediction
# Using data from 2006 onwards
# Xenia: Here, instead of 2006, as the comments said, we are using data from \
# August to October, since 2018 to the current year.
mydata = flow_weekly[
    (flow_weekly['year'] >= 2018) &
    (flow_weekly['month'] <= 10) &
    (flow_weekly['month'] >= 8)][['flow', 'flow_tm1', 'flow_tm2',
                                  'flow_tm3', 'flow_tm4', 'flow_tm5',
                                  'flow_tm6', 'flow_tm7', 'flow_tm8']]

# Seperating initial 80% data for training and rest 20% for testing
trainset = round(0.8*len(mydata))
train = mydata[0:trainset+1][['flow', 'flow_tm1', 'flow_tm2', 'flow_tm3',
                              'flow_tm4', 'flow_tm5', 'flow_tm6', 'flow_tm7',
                              'flow_tm8']]
test = mydata[trainset:][['flow', 'flow_tm1', 'flow_tm2', 'flow_tm3',
                          'flow_tm4', 'flow_tm5', 'flow_tm6', 'flow_tm7',
                          'flow_tm8']]

trainindex = train.index
testindex = train.index
# %%
# Creating function to use Auto-regression model multiple times


def AR_Model(x_train, y_train, x_test, y_test, last_week_flow, trainindex):
    """ Auto-regression model for fotrecasting streamflow

    Parameters
    ----------
    input : arrays and dataframe
    x_train, y_train, x_test, y_test are arrays of training and
    testing datasets while last_week_flow is the dataframe of
    latest flow record. trainindex is general index for training
    data used for plotting as x-axis

    Returns
    ------
    output : type
    Output is printed as flow value of week1 prediction in cfs
    """
    # Fitting AR model to training dataset
    model = LinearRegression().fit(x_train, y_train)

    # Predicting flows using fitted AR model for training dataset
    q_pred_train = model.predict(x_train)

    # Printing model fitting parameters
    r_sq1 = model.score(x_train, y_train)
    print('Training: Coefficient of Determination = ', np.round(r_sq1, 2))
    print('Training: Intercept = ', np.round(model.intercept_, 2))
    print('Training: Slope = ', np.round(model.coef_[0], 2))

    # Plotting flow prediction for training data to visualize model fitting
    fig, ax = plt.subplots()
    ax.plot(trainindex, y_train, label='Observed')
    ax.plot(trainindex, q_pred_train, label='Training')
    ax.set(title="Model Training", xlabel="Date",
           ylabel="Weekly Avg Flow [cfs]", yscale='log')
    ax.legend()
    fig.set_size_inches(8, 3)
    
    # Xenia: Here I just increase the width of the plot from 5 to 8, because
    # the numbers were overlapping.

    # Predicting flows with fitted AR Model
    nextweek_prediction = model.predict(last_week_flow.values)

    # Output of this fuction will be printed as forecasted streamflow
    return nextweek_prediction


# %%
# Using AR_model function to fit different AR models to predict streamflows
# with diffrent inputs

# Model for 1 week prediction using 1-timestep lagged 8 inputs
x1_train = train[['flow_tm1', 'flow_tm2', 'flow_tm3', 'flow_tm4',
                  'flow_tm5', 'flow_tm6', 'flow_tm7', 'flow_tm8']].values
y1_train = train[['flow']].values
x1_test = test[['flow_tm1', 'flow_tm2', 'flow_tm3', 'flow_tm4',
                'flow_tm5', 'flow_tm6', 'flow_tm7', 'flow_tm8']].values
y1_test = test[['flow']].values

last_week_flow = mydata.tail(1)[['flow_tm1', 'flow_tm2', 'flow_tm3',
                                 'flow_tm4', 'flow_tm5', 'flow_tm6',
                                 'flow_tm7', 'flow_tm8']]
model1_pred = AR_Model(x1_train, y1_train, x1_test,
                       y1_test, last_week_flow, trainindex).round(2)

# Xenia: I added above, the round function at the end of model1_pred to avoid
# long numbers.
print('Week 1 Forecast = ', model1_pred[0], 'cfs')

# %%
# Model for 2 week prediction using 2-timestep lagged 4 inputs
x2_train = train[['flow_tm2', 'flow_tm4', 'flow_tm6',
                  'flow_tm8']].values
y2_train = train[['flow']].values
x2_test = test[['flow_tm2', 'flow_tm4', 'flow_tm6',
                'flow_tm8']].values
y2_test = test[['flow']].values

last_week_flow2 = mydata.tail(1)[['flow_tm2', 'flow_tm4', 'flow_tm6',
                                  'flow_tm8']]

model2_pred = AR_Model(x2_train, y2_train, x2_test,
                       y2_test, last_week_flow2, trainindex).round(2)

# Xenia: I added above, the round function at the end of model2_pred to avoid
# long numbers.
print('Week 2 Forecast = ', model2_pred[0], 'cfs')

# %%
# Extra informative plots

# Plotting selected data from entire dataset
# 1. Timeseries of observed flow values
fig, ax = plt.subplots()
ax.plot(flow_weekly['flow'], label='Full data')
ax.plot(mydata['flow'], 'r', label='Selected data')
ax.set(title="Observed Flow", xlabel="Date",
       ylabel="Weekly Avg Flow [cfs]", yscale='log')
ax.legend()
fig.set_size_inches(8, 3)
# fig.savefig("Selected data.png")

# 2. Time series of flow values with the x axis range limited
fig, ax = plt.subplots()
ax.plot(mydata['flow'], label='full')
ax.plot(train['flow'], 'r:', label='training')
ax.set(title="Observed Flow", xlabel="Date", ylabel="Weekly Avg Flow [cfs]",
       yscale='log', xlim=[datetime.date(2018, 8, 1),
                           datetime.date(2020, 10, 10)])
ax.legend()
fig.set_size_inches(8, 3)
# fig.savefig("Zoomed training data.png")

# 3.Plotting training and testing data
fig, ax = plt.subplots()
ax.plot(train.index, train['flow'].values, 'r', label='Training data')
ax.plot(test.index, test['flow'].values, 'g', label='Testing data')
ax.set(title=" Data used for Models", xlabel="Date",
       ylabel="Weekly Avg Flow [cfs]", yscale='log')
ax.legend()
fig.set_size_inches(8, 3)
# fig.savefig("Training-testing data.png")

# %% Printing required answers:
print('AR Model Forecasts for Week 1 = ', model1_pred[0], 'cfs')
print('AR Model Forecasts for Week 2 = ', model2_pred[0], 'cfs')
# My forecast copetition entries are same as AR model predicted streamflows
print('Forecasted flow entries for competition week 1 = ',
      model1_pred[0], 'cfs')
print('Forecasted flow entries for competition week 2 = ',
      model2_pred[0], 'cfs')

# %%
