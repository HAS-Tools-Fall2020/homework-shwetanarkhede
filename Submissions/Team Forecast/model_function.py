# %%
# Alcely: Apparently it must be in the same folder than the main script.
import numpy as np
from sklearn.linear_model import LinearRegression


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
