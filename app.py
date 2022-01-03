import streamlit as st
import pandas as pd
import requests
import json
#import plotly
import plotly.graph_objects as go

# store api key as env variable
from dotenv import load_dotenv
import os
load_dotenv()
vantage_api_key = os.getenv("ALPHAVANTAGE_API_KEY")



st.title("Data Incubator Milestone Project")
st.header("Unadjusted Stock Price Tracker App")

st.write("""
	##### This app retrieves the High, Low, Open, close and Volume data of user choice stock price from Alpha Vantage APIs.  
	""")

st.sidebar.header("User Input Parameter")
select_ticker =  st.sidebar.text_input('Stock ticker','TSLA')



st.write('Ticker:', select_ticker, 'is selected.')



# to get the stock data from alphavantage

@st.cache
def requestData(stock_symbol, vantage_api_key):
	url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&outputsize=full&apikey={}'.format(stock_symbol, vantage_api_key)
	r = requests.get(url)
	data = r.json()
	return  data

stock_data = requestData(select_ticker, vantage_api_key)

if len(stock_data) < 2:
    raise ValueError(f"Give valid stock symbol. {select_ticker} is not valid stock ticker.")



def cleanJsonData(data_json):
	data = pd.DataFrame.from_dict(data_json['Time Series (Daily)'], orient= 'index').sort_index(axis=1)
	data = data.rename(columns={ '1. open': 'Open', '2. high': 'High', '3. low': 'Low', '4. close': 'Close', '5. volume': 'Volume'})
	data = data.apply(pd.to_numeric)
	data.index = pd.to_datetime(data.index)
	data.reset_index(inplace=True)
	data = data.rename(columns = {'index':'Timestamp'})
	return data
	
data_stock = cleanJsonData(stock_data)

# select the year and mont from data and put in the select bar
select_year = st.sidebar.selectbox('Year', tuple(sorted(set(data_stock["Timestamp"].dt.year))))
# select month from only available data


select_month = st.sidebar.selectbox('Month', tuple(sorted(set(data_stock["Timestamp"].dt.month))))

# filter based on select year and month

def filterYearMonth(df_final):
	filter_data = df_final[(df_final["Timestamp"].dt.year == select_year) & (df_final["Timestamp"].dt.month == select_month)]
	return filter_data


st.subheader('Sample of Data')

filter_data = filterYearMonth(data_stock)

if len(filter_data) == 0:
	st.write("""
		#### No data found on this month of your selected year. Choose another month or year!""")

st.dataframe(filter_data.head().reset_index(drop = True))

select_option = st.sidebar.selectbox("Select option you want to plot", ("Select", "Open", "Close", "High", "Low", "Volume"))

# plot the data

if len(filter_data) != 0:

	if select_option in ["Open", "Close", "High", "Low", "Volume"]:

		fig = go.Figure(go.Scatter(
		    x = filter_data['Timestamp'],
		    y = filter_data[select_option],
		))


		fig.update_layout(
		    title={
		        'text': f"{select_option} value of stock {select_ticker}",
		        'y':0.9,
		        'x':0.5,
		        'xanchor': 'center',
		        'yanchor': 'top'},
		         xaxis_title= "Timestamp",
		         yaxis_title= select_option)
		  

		st.plotly_chart(fig, use_container_width=True)
	else:
		st.write(""" 
			##### *Select the option in the sidebar to plot the graph*.
			""")
	
		





