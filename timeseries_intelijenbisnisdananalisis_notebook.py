# -*- coding: utf-8 -*-
"""TimeSeries_IntelijenBisnisdanAnalisis_2008561053.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aqXfVcdZCdu-zLrDKmWNj270ZrrQCCMM
"""

! pip install pmdarima

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

from pmdarima.arima import auto_arima

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

project_data = pd.read_csv('/content/drive/MyDrive/Kaggle/D202.csv')
project_data

project_data['MODIFIED_DATE'] = project_data['DATE']+project_data['START TIME']
project_data.head()

for index, date in enumerate(project_data['DATE']):
    project_data['MODIFIED_DATE'][index] = date+' '+project_data['START TIME'][index]
pd.to_datetime(project_data['MODIFIED_DATE']).head(3)

project_data['MODIFIED_DATE'] = pd.DatetimeIndex(pd.date_range('2016-10-22 00:00:00', periods=len(project_data), freq='min'))
project_data = project_data.set_index('MODIFIED_DATE')
project_data.head()

project_data = project_data.drop(columns=['NOTES'])
project_data.info()

project_data.shape

project_data['YEAR'] = project_data.index.year
project_data['MONTH'] = project_data.index.month
project_data['DAY'] = project_data.index.day
project_data['WEEKDAY'] = project_data.index.day_name()
project_data['WEEKOFYEAR'] = project_data.index.weekofyear
project_data['HOUR'] = project_data.index.hour
project_data['MINUTE'] = project_data.index.minute
project_data.head()

project_data.to_csv('project_data.csv')

transformed_df = project_data.groupby(['DAY']).agg({'USAGE':'sum'})
transformed_df['DAY'] = transformed_df.index
transformed_df.rename(columns={'USAGE':'USAGE'}, inplace=True)

print(transformed_df.shape, transformed_df.columns)

plt.figure(figsize=(15,5))
sns.lineplot(data = transformed_df, x= transformed_df['DAY'], y=transformed_df['USAGE'])
plt.savefig('daily_usage.png')

plt.figure(figsize=(15,5))
pd.plotting.autocorrelation_plot(transformed_df['USAGE'])
print('Autocorrelation = ', round(transformed_df['USAGE'].autocorr(), 2))
plt.savefig('autocorrelation.png')

plot_acf(transformed_df['USAGE'])
plt.grid()
plt.show()
plot_pacf(transformed_df['USAGE'], lags=14)
plt.grid()
plt.show()
plt.savefig('autocorrelation_points.png')

corr = project_data.corr()

plt.figure(figsize=(15,10))
sns.heatmap(corr, annot=True, fmt='.2f', vmin=-1.0, vmax=1.0, center=0)
plt.title('Energy Correlation', fontsize=12);
plt.show()

plt.figure(figsize=(15,10))
sns.heatmap(corr[corr > 0.8], annot=True, vmin=-1.0, vmax=1.0, center=0)
plt.title('Energy Correlation > 80%', fontsize=12);
plt.show()
plt.savefig('energy_correlation.png')

plt.figure(figsize=(15,5))
project_data['USAGE'].resample('D').mean().plot()

# Data resampling by day
data_daily = project_data['USAGE'].resample('d').mean()
rollingMEAN = data_daily.rolling(window=5).mean()
rollingSTD = data_daily.rolling(window=5).std()
#Plot
fig, (ax1, ax2) = plt.subplots(2,1,figsize=(16,6))
plt.subplots_adjust(hspace=0.4)
ax1.plot(data_daily, c='green',label='House overall')
ax1.plot(rollingMEAN, c='blue', label='Rolling mean')
ax2.plot(rollingSTD, c='black',label = 'Rolling Std')

ax1.legend(fontsize=12), ax2.legend(fontsize=12)
ax1.set_ylabel('kW'), ax2.set_ylabel('kW')
ax1.margins(x=0), ax2.margins(x=0)
ax1.grid(), ax2.grid()
plt.savefig('rolling_calculation.png')

result = seasonal_decompose(data_daily, model='additive')
fig = plt.figure()
fig = result.plot()
fig.set_size_inches(10, 10)
plt.savefig('seasonal_decompose.png')

size = int(len(data_daily)*0.7)
train = data_daily[:size]
test = data_daily[size:]

arima_model = auto_arima(train,
                         start_p=0,
                         d=0,
                         start_q=0,
                         max_p=5,
                         max_d=5,
                         max_q=5,
                         start_P=0,
                         D=1,
                         start_Q=0,
                         max_P=5,
                         max_D=5,
                         max_Q=5,
                         m=12, #if m=1 seasonal is set to False
                         seasonal=True,
                         error_action='warn',
                         trace=True,
                         suppress_warnings=True,
                         stepwise=True,
                         random_state=20,
                         n_fits=5 # no of fits is taken as 5 we can increatese this hyperoparam to obtain better result
                        )

arima_model.summary()

arima_model.plot_diagnostics(figsize=(12,9))
plt.savefig('arima_plot.png')

y_forec, conf_int  = arima_model.predict(len(test),return_conf_int=True,alpha=0.05)
pred = pd.Series(y_forec, index=test.index)
pred.columns = ['predicted']
confidence = pd.DataFrame(conf_int, columns=['lower', 'upper'])

plt.figure(figsize=(15,4))
#plt.plot(train, c='green', label='train data')
plt.plot(test, c='blue', label='test data')
plt.plot(pred, c='red', label='predictions')
plt.legend()
plt.grid(), plt.margins(x=0)
plt.title('Results on test data'), plt.xticks(rotation=45)
plt.fill_between(test.index, confidence['lower'],
                 confidence['upper'], color='k', alpha=.15)


from sklearn.metrics import r2_score
print('Actual values: ', np.around(test[:10].tolist(),3))
print('Predictions:   ', np.around(pred[:10].tolist(),3))
print('RMSE: %.3f' % np.sqrt(mean_squared_error(test, pred)))
MAE = mean_absolute_error(test, pred)
MAPE = np.mean(np.abs(pred - test)/np.abs(test))
MASE = np.mean(np.abs(test - pred ))/(np.abs(np.diff(train)).sum()/(len(train)-1))
print('MAE: %.3f' % MAE)
print('MAPE: %.3f' %MAPE)
print('MASE: %.3f' %MASE)
print('R^2 score: %.3f' % r2_score(test, pred))
plt.savefig('arima_pred.png')

from keras.models import Sequential
from keras.layers import Dense, Dropout, Bidirectional, LSTM
n_features = 1
n_steps = 10

lstm_model = Sequential()
lstm_model.add(LSTM(50, activation='relu', input_shape=(n_steps, n_features)))
lstm_model.add(Dense(1))
lstm_model.compile(optimizer='adam', loss='mse')
lstm_model.summary()

def train_test_data(seq, steps):
    X, Y = list(), list()
    for i in range(len(seq)):
        sample = i + steps
        if sample > len(seq)-1:
            break
        x, y = seq[i:sample],seq[sample]
        X.append(x)
        Y.append(y)
    return np.array(X), np.array(Y)
def train_test_validation_plot(train_size, test_size):
    plt.figure(figsize=(12,9))
    plt.plot(data_daily[:train_size])
    plt.plot(data_daily[train_size:test_size])
    plt.plot(data_daily[test_size:])
steps = 10
X, Y = train_test_data(data_daily.tolist(), steps)
X = X.reshape((X.shape[0], X.shape[1], 1))

Training_size = int(len(data_daily)*0.7)
Training_Validation_size = int(((len(data_daily)-size)/2)+size)
#Training_Test_size = int(len(data_daily)*0.3)

X_train, Y_train = X[:Training_size], Y[:Training_size]
X_val, Y_val = X[Training_size:Training_Validation_size], Y[Training_size:Training_Validation_size]
X_test, Y_test = X[Training_size:Training_Validation_size], Y[Training_size:Training_Validation_size]

print('Training size:', Training_size)
print('Training + Validation size:', Training_Validation_size)

train_test_validation_plot(Training_size, Training_Validation_size)

mse_train = list()
mse_val = list()

for epoch in range(0,50,5):
    # fit the model with epochs
    model_fit = lstm_model.fit(X_train, Y_train, epochs=epoch, verbose=1)

    #model evaluation
    Train_pred = lstm_model.predict(X_train, verbose=0)
    Val_pred = lstm_model.predict(X_val, verbose=0)

    #computing the training and validation loss
    mse_t = mean_squared_error(Train_pred, Y_train)
    mse_v = mean_squared_error(Val_pred, Y_val)
    mse_train.append(mse_t)
    mse_val.append(mse_v)

# Plot the loss results
def plot_loss_results(mse_train, mse_val):
    plt.plot(range(0,50,5), mse_train, label='Train loss')
    plt.plot(range(0,50,5), mse_val,  label='Validation loss')
    plt.legend()
    print('Train MSE minimum:', min(mse_train))
    print('Validation MSE minimum:', min(mse_val))
plot_loss_results(mse_train, mse_val)

plt.plot(model_fit.history['loss'], label='Train loss')
plt.legend()
print('Train MSE minimum:', min(model_fit.history['loss']))

from keras.models import load_model

lstm_model.save('my_model.h5')

Train_pred = lstm_model.predict(X_train, verbose=0)
Y_pred = lstm_model.predict(X_test, verbose=0)

Y_pred_series = pd.Series(Y_pred.flatten().tolist(), index=data_daily[size+(np.abs(len(Y_pred.flatten().tolist()) - len(data_daily[size:].index))):].index)
Train_pred_series = pd.Series(Train_pred.flatten().tolist(), index=data_daily[:size].index)

#Plot
plt.figure(figsize=(15,4))
plt.plot(data_daily[:size], c='blue',label='train data')
plt.plot(Train_pred_series, c='green',label='train predicted data')
#plt.plot(data_daily[size:], c='black',label='test data')
#plt.plot(Y_pred_series, c='red', label='model')
plt.legend()
plt.grid(), plt.margins(x=0);

# calc error
print('MSE: %.5f' % (mean_squared_error(Y_pred, Y_test)))
print('RMSE: %.5f' % np.sqrt(mean_squared_error(Y_pred, Y_test)))
MAE = mean_absolute_error(Y_test, Y_pred)
MAPE = np.mean(np.abs(Y_pred - Y_test)/np.abs(Y_test))
print('MAE: %.3f' % MAE)
print('MAPE: %.3f' %MAPE)
print('MASE: %.3f' %MASE)
print('R^2 score: %.3f' % r2_score(Y_test, Y_pred))
plt.savefig('lstm_pred.png')