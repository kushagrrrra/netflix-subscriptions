import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.express as px
import plotly.io as pio
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import streamlit as st

# Set the Streamlit template to "wide"
st.set_page_config(layout="wide")

# Title and description
st.title("Netflix Subscription Forecasting")
st.markdown("This app forecasts the number of Netflix subscriptions for the next quarters using ARIMA.")

# Load the data
data = pd.read_csv('Netflix-Subscriptions.csv')

# Convert Time Period to datetime
data['Time Period'] = pd.to_datetime(data['Time Period'], format='%d/%m/%Y')

# Sidebar
st.sidebar.header("Select Forecasting Parameters")

# Order selection
p = st.sidebar.slider("p (AR order)", 0, 5, 1)
d = st.sidebar.slider("d (Difference order)", 0, 2, 1)
q = st.sidebar.slider("q (MA order)", 0, 5, 1)

# Forecasting
st.sidebar.header("Make Forecasts")
future_steps = st.sidebar.slider("Number of Quarters to Forecast", 1, 10, 5)

# Calculate differenced series
differenced_series = data['Subscribers'].diff().dropna()

# Fit ARIMA model
model = ARIMA(differenced_series, order=(p, d, q))
results = model.fit()

# Make forecasts
start = len(differenced_series)
end = start + future_steps - 1
forecast_diff = results.predict(start=start, end=end, typ='levels').rename('Forecast')

# Inverse difference to get actual forecast values
forecast = pd.concat([differenced_series, forecast_diff]).cumsum().rename('Forecast')

# Plot the forecast
fig = go.Figure()
fig.add_trace(go.Scatter(x=data['Time Period'], y=data['Subscribers'], mode='lines', name='Original Data'))
fig.add_trace(go.Scatter(x=forecast.index[-future_steps:], y=forecast[-future_steps:], mode='lines', name='Forecast'))
fig.update_layout(title='Netflix Quarterly Subscription Forecast',
                  xaxis_title='Time Period',
                  yaxis_title='Subscribers')
st.plotly_chart(fig, use_container_width=True)

# Display forecast table
st.header("Forecasted Subscription Counts")
forecast_table = pd.DataFrame({'Time Period': [data['Time Period'].iloc[-1] + pd.DateOffset(months=i*3) for i in range(1, future_steps + 1)]})
forecast_table['Forecast'] = forecast.iloc[-future_steps:].values.round(0).astype(int)
st.write(forecast_table)

# ACF and PACF plots
st.sidebar.header("ACF and PACF Plots")

# Calculate ACF and PACF
fig_acf, ax_acf = plt.subplots(figsize=(8, 4))
plot_acf(differenced_series, ax=ax_acf)
ax_acf.set_title('Autocorrelation Function (ACF)')

fig_pacf, ax_pacf = plt.subplots(figsize=(8, 4))
plot_pacf(differenced_series, ax=ax_pacf)
ax_pacf.set_title('Partial Autocorrelation Function (PACF)')

st.pyplot(fig_acf)
st.pyplot(fig_pacf)

# Data source
st.sidebar.header("Data Source")
st.sidebar.info("The data used in this app is from a fictional dataset of Netflix subscriptions growth.")

# Data table
st.header("Netflix Subscription Data")
st.write(data)

# About section
st.sidebar.header("About")
st.sidebar.info("This Streamlit app is created to demonstrate time series forecasting with ARIMA.")
