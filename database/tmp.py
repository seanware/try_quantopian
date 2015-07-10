import math
import numpy as np
import pandas as pd

import pandas.io.data as web
import plotly.plotly as py
import matplotlib.pyplot as plt

# %matplotlib inline
import requests
import datetime

from plotly.graph_objs import *

import mpt

from database import Database
db = Database()

date_range = {"start": datetime.date(2009,1,1), "end": datetime.date(2012,12,31)}

chicago_companies = ['ADM',  'BA', 'MDLZ', 'ALL', 'MCD', 'EXC', 'ABT',
                     'KRFT', 'ITW', 'GWW',  'DFS', 'DOV', 'MSI',
                     'NI', 'TEG', 'CF' ]
chicago_returns = db.select(('SELECT dt, "{}" FROM return'
                             ' WHERE dt BETWEEN ''%s'' AND ''%s'''
                             ' ORDER BY dt;').format(
                             '", "'.join((c.lower() for c in chicago_companies))),
                            columns=["Date"] + chicago_companies,
                            args=[date_range['start'], date_range['end']])

# At this point chicago_returns is an array of dictionaries
# [{"Date":datetime.date(2009,1,1), "ADM":0.1, "BA":0.2, etc ... , "CF": 0.1},
#  {"Date":datetime.date(2009,1,2), "ADM":0.2, "BA":0.1, etc ..., "CF":0.1},
#  ...,
#  {"Date":datetime.date(2012,12,31), "ADM":0.2, "BA":0.1, etc ..., "CF":0.1}]


# Pull out the dates to mak them the indices in the Pandas DataFrame
chi_dates = [row.pop("Date") for row in chicago_returns]
chicago_returns = pd.DataFrame(chicago_returns, index=chi_dates)
chicago_returns = chicago_returns / 100

# treas90 = web.DataReader('^IRX', 'yahoo', date_range['start'], date_range['end'])
# treas90['treas90'] = treas90['Adj Close'].diff() / treas90['Adj Close']
# chicago_returns = chicago_returns.join(treas90['treas90'])

chicago_returns.drop(chicago_returns.head(1).index, inplace=True)
chicago_returns.replace([np.inf, -np.inf], np.nan, inplace=True)
result = mpt.get_efficient_frontier(chicago_returns)


# Be sure to annualize the returns
sds = list(chicago_returns.std()*math.sqrt(250)) + [0]
mus = list((1+chicago_returns.mean())**250-1) + [0.005]
syms = list(chicago_returns.columns) + ['treas90']

frontier = Scatter(x=result.returns, y=result.risks, mode="lines")
symbols = Scatter(x=mus, y=sds, mode='text', text=syms)

fig = Figure(data=[frontier, symbols])
frontier_url = py.plot(fig, filename="Efficient Frontier")

# Exelon (EXC) looks odd because the annual returns are negative.
# I don't know whether it's good to trust that it will continue to fall.
# It turned around in 2013 -- actually the plot below doesn't go that far...
#     Yahoo: http://finance.yahoo.com/echarts?s=EXC
#
exc = Scatter(
        x=chicago_returns.index, y=chicago_returns.EXC,
        name="Exelon daily return",
        mode="lines")
exc_cum_avg = [sum(chicago_returns.EXC[:(n+1)])/(n+1) for n in range(len(chicago_returns.EXC))]
exc_cum_avg = Scatter(
        x=chicago_returns.index, y=exc_cum_avg,
        name="cumulative average",
        mode="lines",
        line=Line(color="rgb(242, 8, 8)"))
fig = Figure(data=[exc, exc_cum_avg])
exc_url = py.plot(fig, filename="Exelon returns")


# Let's remove it because it ruins the efficient frontier.
# (pushes it out way to the left) 

