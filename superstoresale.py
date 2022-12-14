# -*- coding: utf-8 -*-
"""superstoresale.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1i0-ZnX3AFf_9dBzYl9D4HDotAYPx7vYR

**Importing necessary library**
"""

import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import matplotlib

plt.style.use('fivethirtyeight')
matplotlib.rcParams['axes.labelsize'] = 13
matplotlib.rcParams['xtick.labelsize'] = 11
matplotlib.rcParams['ytick.labelsize'] = 11
matplotlib.rcParams['text.color'] = 'b'

pip install --upgrade xlrd

"""**Dataset Loading**"""

sale = pd.read_excel('/content/Sample - Superstore.xls')
sale

#sdescription of the dataset with numeric entries in it.
sale.describe()

"""**Data Cleaning.**"""

#removing the columns not required for forecasting.

cols = ['Row ID', 'Order ID', 'Ship Date', 'Ship Mode', 'Customer ID', 'Customer Name', 'Segment', 'Country', 'City', 'State', 'Postal Code', 'Region', 'Product ID', 'Category', 'Sub-Category', 'Product Name', 'Quantity', 'Discount', 'Profit']
sale.drop(cols, axis = 1, inplace = True)

#displaying the data after removing the columns.
sale

#checking for null values
sale.isnull().sum()

#Sorting the Order Date 
sale = sale.sort_values('Order Date')

#grouping sales according to Order Date
sale.groupby('Order Date')['Sales'].sum().reset_index()

#displaying the min and max values of Order Date
print(sale['Order Date'].min())
print(sale['Order Date'].max())

#setting the 'Order Date' as index
sale = sale.set_index('Order Date')
sale.index

#calculating the average the daily sales value for each month and using it at start of each month as the timestamp
df = sale['Sales'].resample('MS').mean()
df['2017':]

"""**Time series forecasting with ARIMA model**"""

#setting the typical ranges for p, d, q
p = d = q = range(0, 2)

#taking and setting all possible combination for p, d and q
ar = list(itertools.product(p, d, q))
seasonal_ar = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]

#Using the Grid Search find the optimal set of parameters that yields the best performance
for parameter in ar:
    for parameter_seasonal in seasonal_ar:
        try:
            model = sm.tsa.statespace.SARIMAX(df, order = parameter, seasonal_order = parameter_seasonal, enforce_stationary = False,enforce_invertibility=False) 
            result = model.fit()   
            print('ARIMA{}x{}12 - AIC:{}'.format(parameter, parameter_seasonal, result.aic))
        except:
            continue

"""**fitting the ARIMA model**

"""

model_ar = sm.tsa.statespace.SARIMAX(df, order = (1, 1, 1),
                                  seasonal_order = (1, 1, 0, 12)
                                 )
result = model_ar.fit()
print(result.summary().tables[1])

"""**validate the forecasts**"""

predict = result.get_prediction(start = pd.to_datetime('2017-01-01'), dynamic = False)
predict_ci = predict.conf_int()
predict_ci

#Visualization of the forecaste
ax = df['2014':].plot(label = 'observed')
predict.predicted_mean.plot(ax = ax, label = 'One-step Ahead Forecast', alpha = 0.7, figsize = (14, 7))
ax.fill_between(predict_ci.index, predict_ci.iloc[:, 0], predict_ci.iloc[:, 1], color = 'k', alpha = 0.2)
ax.set_xlabel("Date")
ax.set_ylabel('Furniture Sales')
plt.legend()
plt.show()

#Evaluating the metrics
df_hat = predict.predicted_mean
df_truth = df['2017-01-01':]

mse = ((df_hat - df_truth) ** 2).mean()
rmse = np.sqrt(mse)
print('The Mean Squared Error of our forecasts is {}'.format(round(mse, 2)))
print('The Root Mean Squared Error of our forecasts is {}'.format(round(rmse, 2)))

#forcasting the data
pred_uc = result.get_forecast(steps = 100)
pred_ci = pred_uc.conf_int()

ax = df.plot(label = 'observed', figsize = (14, 7))
pred_uc.predicted_mean.plot(ax = ax, label = 'forecast')
ax.fill_between(pred_ci.index, pred_ci.iloc[:, 0], pred_ci.iloc[:, 1], color = 'k', alpha = 0.25)
ax.set_xlabel('Date')
ax.set_ylabel('Furniture Sales')

plt.legend()
plt.show()