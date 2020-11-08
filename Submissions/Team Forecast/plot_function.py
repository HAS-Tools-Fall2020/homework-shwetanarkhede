# %%

import pandas as pd
import matplotlib.pyplot as plt

# %%


def hist_daily_mean(data, end_year):
    """ Calculates the historical daily flow mean.
    ----------
    Parameters:
    data: dataframe
          input data with year, month, day and flow columns.
    end_year: integer
              last year (no inclusive) as historical flow.
    ----------
    Returns:
    hist_flow: dataframe
    """
    hist_flow = pd.DataFrame(columns=['month', 'day', 'flow'])
    for m in range(12):
        if m == 1:
            days = 29

        if m == 3 or m == 5 or m == 8 or m == 10:
            days = 30

        if m == 0 or m == 2 or m == 4 or m == 6 or m == 7 or m == 9 or m == 11:
            days = 31

        for i in range(days):
            hist_flow = hist_flow.append({
                        'month': (m+1), 'day': (i+1),
                        'flow': round(
                            data[(data['year'] != end_year) &
                                 (data['month'] == m+1) &
                                 (data['day'] == i+1)]['flow'].mean(), 3)},
                        ignore_index=True)
    return hist_flow

# %%


def weekly_mean(data, fmonth, fday, weeks, year=None):
    """Calculates the weekly flow mean since the input date
    for a number of weeks. Useful when don't have a datetime column.
    ----------
    Parameters:
    data: dataframe
          input data with year(optional), month, day and flow columns.
    fmonth: integer
            first month of the first week.
    fday: integer
          first day of the first week.
    weeks: integer
           number of weeks for calculate the weekly mean.
    year: integer
          a specific year.
    ----------
    Returns:
    week_mean: dataframe
    """
    week_mean = []
    for i in range(16):
        eday = (fday + 6)
        if eday > 31:
            eday = (eday-31) + (6-(eday-31))
            fmonth += 1

        if year is None:
            if eday > fday:
                meandata = data[(data["month"] == fmonth) &
                                (data["day"] >= fday) &
                                (data["day"] <= eday)]["flow"].mean()
            else:
                meandata = (data[(data["month"] == fmonth-1) &
                                 (data["day"] >= fday)]["flow"].mean() +
                            data[(data["month"] == fmonth) &
                                 (data["day"] <= eday)]["flow"].mean())/2
        else:
            if eday > fday:
                meandata = data[(data["year"] == year) &
                                (data["month"] == fmonth) &
                                (data["day"] >= fday) &
                                (data["day"] <= eday)]["flow"].mean()
            else:
                meandata = (data[(data["year"] == year) &
                                 (data["month"] == fmonth-1) &
                                 (data["day"] >= fday)]["flow"].mean() +
                            data[(data["year"] == year) &
                                 (data["month"] == fmonth) &
                                 (data["day"] <= eday)]["flow"].mean())/2
        week_mean.append(round(meandata, 3))
        fday = eday + 1

    return week_mean

# %%


def plot_3series(historical, observed, predicted, observed_year):
    """ generates a line plot with 3 time series
    ----------
    Parameters:
    historical, observed, predicted: dataframe, array or list.
    Contains the series to plot.

    observed_year: integer.
    Specify the observed serie year.
    ----------
    Returns: shows and saves the plot figure.
    """
    plt.style.use('seaborn')

    fig, ax = plt.subplots()
    ax.plot(historical, color='black', label='Historical Mean')
    ax.plot(observed, color='blue', label=str(observed_year)+' weekly flows')
    ax.plot(predicted, color='black', label='weekly predicted flows',
            linestyle="--")
    ax.set(title="Observed & Predicted Flow", xlabel="Weeks", 
           ylabel="Weekly Avg Flow [cfs]",
           yscale='log')
    ax.legend()

    fig.savefig('plot.png')

# %%
