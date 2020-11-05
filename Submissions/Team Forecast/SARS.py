# Homework Assignment # 9 (Week 9)
# Modified by : Shweta Narkhede
# Last modified on: Oct 25th, 2020


# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import urllib.request as req
import urllib
import model_function as mf
from sklearn.linear_model import LinearRegression
# %%
# Getting data from MesoWest

# Creating the URL for the rest API using token
mytoken = 'demotoken'  # '9b2f7a84186d4f70b31786c32f4032bb'

# Base url
base_url = "http://api.mesowest.net/v2/stations/timeseries"

# Specific arguments for the data that we want
args = {
    'start': '200001010000',
    'end': '202010240000',
    'obtimezone': 'UTC',
    'vars': 'precip_accum',
    'stids': 'QVDA3',
    'units': 'precip|in',
    'token': mytoken}

apiString = urllib.parse.urlencode(args)
print(apiString)

# adding the API string to the base_url
fullUrl = base_url + '?' + apiString
print(fullUrl)

# Requesting data and reading it in complete format
response = req.urlopen(fullUrl)
responseDict = json.loads(response.read())

# Keys shows you the main elements of your dictionary
responseDict.keys()
responseDict['UNITS']

# Each key in the dictionary can link to different data structures
type(responseDict['UNITS'])
responseDict['UNITS'].keys()
responseDict['UNITS']['precip_accum']

# If we grab the first element of the list that is a dictionary
type(responseDict['STATION'][0])
# And these are its keys
responseDict['STATION'][0].keys()

# Getting precipitation data that we wanted from website
dateTime = responseDict['STATION'][0]['OBSERVATIONS']['date_time']
precip = responseDict['STATION'][0]['OBSERVATIONS']['precip_accum_set_1']

# Combining precipitation data and date index into a dataframe
data = pd.DataFrame({'Precipitation': precip}, index=pd.to_datetime(dateTime))

# Converting data to weekly average
precip_weekly = data.resample('W').mean()
ptindex = precip_weekly.index

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

# (I tried to put this function in seperate script, but then it gives me an
# error of undefined name LinerRegression)
# Creating empty dataframe for storing predicted flows
predicted_flows = pd.DataFrame(columns=["Week", "Flow"])


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


# For loop for making predictions for 16 weeks
for i in range(16):
    x1 = mydata[lag_cols].values
    y1 = mydata[['flow']].values
    last_week_flow = mydata.tail(1)[lag_cols]
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
