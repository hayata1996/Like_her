import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import random
from datetime import datetime, timedelta

def get_stock_data():
    """Fetch stock data from API or fallback to generated data if API fails"""
    api_url = "http://api:8000/stocks"
    
    try:
        # Get stock symbol from session state if available
        symbol = st.session_state.get('stock_symbol', '7974.T')  # Default to Nintendo
        
        # Make API request with the selected stock symbol
        response = requests.get(f"{api_url}?symbol={symbol}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data['data'])
            
            # Ensure proper date format
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Add symbol information
            df['Symbol'] = symbol
            
            return df
        else:
            st.error(f"Failed to fetch stock data: {response.status_code}")
            # Return fallback data for demonstration
            return get_fallback_stock_data()
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        # Return fallback data for demonstration
        return get_fallback_stock_data()

def get_fallback_stock_data():
    """Generate fallback stock data when API is unavailable"""
    # Create a date range for the past 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')
    
    # Generate random stock data
    base_price = 60000  # Starting price
    price_range = 5000  # Max fluctuation
    
    data = []
    close_price = base_price
    
    for date in date_range:
        # Generate realistic price movements
        open_price = close_price
        high_price = open_price * (1 + (random.uniform(0, 0.03)))
        low_price = open_price * (1 - (random.uniform(0, 0.03)))
        close_price = random.uniform(low_price, high_price)
        volume = int(random.uniform(100000, 1000000))
        
        data.append({
            'Date': date,
            'Open': open_price,
            'High': high_price,
            'Low': low_price,
            'Close': close_price,
            'Volume': volume
        })
    
    df = pd.DataFrame(data)
    
    # Calculate moving averages
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['Symbol'] = '7974.T'
    
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
        st.button("Refresh Data", on_click=lambda: st.session_state.update({'refresh_stocks': True}))
    
    # Fetch stock data
    df = get_stock_data()
    
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
        xaxis_title='Date',
        yaxis_title='Price (¥)',
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
        
        **Latest Date:** {latest_date.strftime('%Y-%m-%d')}
        
        **Latest Price:** ¥{latest_data['Close']:,.2f}
        
        **Change:** {(latest_data['Close'] - latest_data['Open']) / latest_data['Open'] * 100:.2f}%
        
        **30-day Range:** ¥{df['Low'].min():,.2f} - ¥{df['High'].max():,.2f}
        """)