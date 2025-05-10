import yfinance as yf
from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import random
import json
import logging
import sys
import os


# Base directory for data storage
DATA_DIR = os.environ.get("DATA_DIR", "/data")
MODEL_PATH = os.environ.get("MODEL_PATH", "/data/models")

# AI Platform configuration
PROJECT_ID = os.environ.get("PROJECT_ID")
LOCATION = os.environ.get("LOCATION", "us-central1")
AGENT_ID = os.environ.get("AGENT_ID")

def main(symbol):
    period = "1mo"  # You can change this to "1d", "5d", "1y", etc.
    print(f"Testing yfinance with symbol: {symbol}")
    try:
        # Use yfinance to get real stock data
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        
        # Reset index to make date a column
        hist.reset_index(inplace=True)
        
        # Convert datetime to string for JSON serialization
        hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')
        
        # Add moving averages
        hist['MA5'] = hist['Close'].rolling(window=5).mean()
        hist['MA20'] = hist['Close'].rolling(window=20).mean()
        
        # Get company name
        info = stock.info
        company_name = info.get('shortName', symbol)
        
        # Convert to dict for JSON response
        data = {
            "Date": hist['Date'].tolist(),
            "Open": hist['Open'].tolist(),
            "High": hist['High'].tolist(),
            "Low": hist['Low'].tolist(),
            "Close": hist['Close'].tolist(),
            "Volume": hist['Volume'].tolist(),
            "MA5": hist['MA5'].tolist(),
            "MA20": hist['MA20'].tolist(),
            "Symbol": symbol,
            "Name": company_name
        }
        return data
    
    except Exception as e:
        print(f"❌ Error fetching data from yfinance: {e}")

def get_stock_data(symbol):
    """Fetch stock data from API or fallback to generated data if API fails"""
    st.session_state['stock_symbol'] = symbol
    
    data = main(symbol)
    
    if not data:
        raise RuntimeError(f"No data returned for symbol {symbol}")
    # Create DataFrame
    df = pd.DataFrame(data)
    # unify date column name (handle 'Date', 'dates', 'date')
    date_cols = [col for col in df.columns if col.lower() == 'date']
    if date_cols:
        df.rename(columns={date_cols[0]: 'Date'}, inplace=True)
    else:
        raise KeyError("'Date' column not found in stock data; got columns: %s" % list(df.columns))
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Add symbol information
    df['Symbol'] = symbol
    print(f"Fetched data for {symbol}: {df.head()}")
    
    return df


def display_stock_chart():
    """Display stock chart with input controls"""
    st.subheader("Stock Price Analysis")
    
    # Stock symbol input
    col1, col2 = st.columns([3, 1])
    with col1:
        symbol = st.text_input("Stock Symbol", 
                              value=st.session_state.get('stock_symbol', '7974.T'),
                              help="Enter stock symbol (e.g., AAPL for Apple, 7974.T for Nintendo)")
    with col2:
        st.session_state['stock_symbol'] = symbol
        # Debug: show current session state
        st.write("Session State:", dict(st.session_state))
        st.button("Refresh Data", on_click=lambda: st.session_state.update({'refresh_stocks': True}))
    
    # Fetch stock data
    try:
        df = get_stock_data(symbol)
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        return
    
    print(f"Fetched data for df['Date']: {df['Date'].head()}")
    
    # Create candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    )])
    
    # Add moving averages if they exist
    if 'MA5' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['Date'], 
            y=df['MA5'], 
            mode='lines',
            line=dict(color='blue', width=1),
            name='MA5'
        ))
    
    if 'MA20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['Date'], 
            y=df['MA20'], 
            mode='lines',
            line=dict(color='orange', width=1),
            name='MA20'
        ))
    
    # Update layout
    fig.update_layout(
        title=f"{df['Symbol'].iloc[0]} Stock Price",
        xaxis_title='date',
        yaxis_title='Price ()',
        plot_bgcolor='#1E1E1E',
        paper_bgcolor='#1E1E1E',
        font=dict(color='#00FF00'),
        xaxis=dict(
            showgrid=True,
            gridcolor='#333333',
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#333333',
        ),
        legend=dict(
            font=dict(color='#00FF00')
        ),
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display summary statistics
    with st.expander("Stock Data Summary"):
        latest_date = df['Date'].max()
        latest_data = df[df['Date'] == latest_date].iloc[0]
        
        st.markdown(f"""
        **Symbol:** {df['Symbol'].iloc[0]}
        
        **Latest date:** {latest_date.strftime('%Y-%m-%d')}
        
        **Latest Price:** {latest_data['Close']:,.2f}
        
        **Change:** {(latest_data['Close'] - latest_data['Open']) / latest_data['Open'] * 100:.2f}%
        
        **30-day Range:** {df['Low'].min():,.2f} - {df['High'].max():,.2f}
        """)


if __name__ == "__main__":
    display_stock_chart()