import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import requests
import os
import time
import json
from io import BytesIO
import base64
from datetime import datetime, timedelta
import random
import subprocess

# No speech processing libraries needed - using Gemini API instead
VOICE_FEATURES_ENABLED = True

# Set page configuration
st.set_page_config(
    page_title="Like Her - AI Assistant",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for terminal-like interface
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
        color: #00FF00;
    }
    .stTextInput>div>div>input {
        background-color: #1E1E1E;
        color: #00FF00;
        font-family: 'Courier New', Courier, monospace;
        border: 1px solid #00FF00;
    }
    .stButton>button {
        background-color: #1E1E1E;
        color: #00FF00;
        font-family: 'Courier New', Courier, monospace;
        border: 1px solid #00FF00;
    }
    .terminal-text {
        background-color: #1E1E1E;
        color: #00FF00;
        font-family: 'Courier New', Courier, monospace;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #00FF00;
        overflow-y: auto;
        height: 400px;
    }
    .chat-message {
        padding: 5px;
        border-radius: 3px;
        margin-bottom: 5px;
        font-family: 'Courier New', Courier, monospace;
    }
    .user-message {
        background-color: #2E2E2E;
        margin-left: 20px;
    }
    .assistant-message {
        background-color: #1E1E1E;
        margin-right: 20px;
        border-left: 2px solid #00FF00;
    }
    .emphasis {
        color: #FF00FF;
        font-weight: bold;
    }
    .stPlotlyChart {
        background-color: #1E1E1E;
        border: 1px solid #00FF00;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for conversation history
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

if 'system_message' not in st.session_state:
    current_time = datetime.now().strftime("%H:%M:%S")
    greeting = f"[{current_time}] System initialized. Hello, I'm your personal AI assistant."
    st.session_state.system_message = greeting
    st.session_state.conversation.append({"role": "assistant", "content": greeting})

# API URL (default for local development, can be overridden by environment)
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# Function to autoplay audio
def autoplay_audio(audio_data):
    if not VOICE_FEATURES_ENABLED:
        return
        
    b64 = base64.b64encode(audio_data).decode()
    md = f"""
        <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

# Function to convert text to speech (placeholder - not using gTTS anymore)
def text_to_speech(text):
    # We're not using gTTS anymore, so just return None
    return None

# Function to display terminal-like text
def display_terminal():
    terminal_html = "<div class='terminal-text'>"
    for message in st.session_state.conversation:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            terminal_html += f"<div class='chat-message user-message'>> {content}</div>"
        else:
            terminal_html += f"<div class='chat-message assistant-message'>{content}</div>"
    
    terminal_html += "</div>"
    st.markdown(terminal_html, unsafe_allow_html=True)

# Function for speech recognition (placeholder - no longer using speech_recognition)
def speech_to_text(audio_data):
    # We're not using speech_recognition anymore, so just return None
    return None

# Function to fetch stock data from API
def get_stock_data():
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

# Fallback function for when API is unavailable
def get_fallback_stock_data():
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

# Function to display stock chart
def display_stock_chart():
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
    
    if df is not None and not df.empty:
        # Create a candlestick chart with Plotly
        fig = go.Figure()
        
        # Add candlestick chart
        fig.add_trace(go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price',
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ))
        
        # Add 5-day moving average
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['MA5'],
            mode='lines',
            line=dict(color='blue', width=1),
            name='5-Day MA'
        ))
        
        # Add 20-day moving average
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['MA20'],
            mode='lines',
            line=dict(color='orange', width=1),
            name='20-Day MA'
        ))
        
        # Add volume as a bar chart at the bottom with lower opacity
        fig.add_trace(go.Bar(
            x=df['Date'],
            y=df['Volume'],
            name='Volume',
            marker_color='rgba(100, 100, 100, 0.3)',
            yaxis='y2'
        ))
        
        # Set title and layout
        symbol_name = df['Symbol'].iloc[0] if 'Symbol' in df.columns else 'Stock'
        fig.update_layout(
            title=f'{symbol_name} Stock Price',
            xaxis_title='Date',
            yaxis_title='Price',
            xaxis_rangeslider_visible=False,
            yaxis2=dict(
                title='Volume',
                overlaying='y',
                side='right',
                showgrid=False
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            height=600,
            hovermode='x unified',
            template='plotly_white'
        )
        
        # Display the interactive chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Display key statistics
        with st.expander("Stock Statistics"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current Price", f"¥{df['Close'].iloc[-1]:,.0f}")
            with col2:
                price_change = df['Close'].iloc[-1] - df['Close'].iloc[-2]
                percent_change = (price_change / df['Close'].iloc[-2]) * 100
                st.metric("Change", f"¥{price_change:,.0f}", f"{percent_change:.2f}%")
            with col3:
                st.metric("Volume", f"{df['Volume'].iloc[-1]:,.0f}")
            with col4:
                highest = df['High'].max()
                st.metric("30-Day High", f"¥{highest:,.0f}")
            
            # Show recent data in a table
            st.subheader("Recent Data")
            display_df = df.tail(5).copy()
            display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
            for col in ['Open', 'High', 'Low', 'Close', 'MA5', 'MA20']:
                if col in display_df.columns:
                    display_df[col] = display_df[col].map('¥{:,.0f}'.format)
            if 'Volume' in display_df.columns:
                display_df['Volume'] = display_df['Volume'].map('{:,.0f}'.format)
            st.dataframe(display_df.iloc[::-1], use_container_width=True)
    else:
        st.error("No stock data available to display")

# Function to handle chat interaction
def chat_with_ai(input_text):
    current_time = datetime.now().strftime("%H:%M:%S")
    
    # Add user message to conversation
    st.session_state.conversation.append({"role": "user", "content": input_text})
    
    try:
        # In a real implementation, this would call your API
        # response = requests.post(f"{API_URL}/chat", json={"message": input_text})
        # response_text = response.json()["response"]
        
        # For now, let's use a mock response
        time.sleep(1)  # Simulate API call delay
        response_text = f"[{current_time}] I received your message: '{input_text}'. This is a placeholder response. In the final version, this would be powered by the Swallow1.5 LLM."
        
        # Add AI response to conversation
        st.session_state.conversation.append({"role": "assistant", "content": response_text})
        
    except Exception as e:
        error_message = f"[{current_time}] Error: Could not process your request. {str(e)}"
        st.session_state.conversation.append({"role": "assistant", "content": error_message})

# Function to get AI news (placeholder)
def get_ai_news():
    # This is a placeholder. In production, you'd fetch real news from an API
    return [
        {
            "title": "Google DeepMind Announces New AI Architecture",
            "summary": "A breakthrough in AI architecture that improves efficiency by 40%.",
            "date": "2025-04-20"
        },
        {
            "title": "Sakana AI Releases Expanded Version of Swallow Model",
            "summary": "Japanese AI startup Sakana AI has released Swallow 2.0 with improved language capabilities.",
            "date": "2025-04-19"
        },
        {
            "title": "AI Regulation Framework Proposed in EU",
            "summary": "New regulations aim to ensure ethical AI development across European markets.",
            "date": "2025-04-18"
        }
    ]

# Create the main layout
st.title("Like Her - Your Personal AI Assistant")

# Create two columns for the layout
col1, col2 = st.columns([1, 1])

with col1:
    # Display the terminal-like conversation interface
    display_terminal()
    
    # Text input for chat
    user_input = st.text_input("Enter your message:", key="user_input")
    
    # Voice input using native st.audio_input
    st.write("Or record your voice:")
    audio_bytes = st.audio_input("Record your voice")
    
    if audio_bytes:
        # Save audio as mp3 file for sending to Gemini API
        temp_file_path = "temp_audio.mp3"
        # Read the data from the UploadedFile object before writing to file
        with open(temp_file_path, "wb") as f:
            f.write(audio_bytes.getvalue())
        
        # Here you would send the audio file to Gemini API
        # For now, just display a message
        st.info(f"Audio saved to {temp_file_path}. Ready to send to Gemini API.")
        
        # TODO: Implement the Gemini API call here
        # Example pseudocode:
        # response = send_audio_to_gemini_api(temp_file_path)
        # if response:
        #     chat_with_ai(response["transcription"])
        #     # Clear the input
        #     st.rerun()
    
    if user_input:
        chat_with_ai(user_input)
        # Clear the input box
        st.rerun()

with col2:
    # AI News section
    st.subheader("AI Industry News")
    news = get_ai_news()
    for item in news:
        st.markdown(f"""
        <div style='background-color: #1E1E1E; padding: 10px; margin-bottom: 10px; border-left: 2px solid #00FF00;'>
            <p style='color: #FF00FF; margin-bottom: 5px;'>{item['title']}</p>
            <p style='color: #00FF00; font-size: 0.8em;'>{item['summary']}</p>
            <p style='color: #888888; font-size: 0.7em;'>{item['date']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Stock chart section
    st.subheader("AI Stock Tracker")
    display_stock_chart()
    
    # Health data summary (placeholder)
    st.subheader("Health Summary")
    st.markdown("""
    <div style='background-color: #1E1E1E; padding: 10px; border-left: 2px solid #00FF00;'>
        <p style='color: #00FF00;'>Last sync: 2025-04-21 06:30 AM</p>
        <p style='color: #00FF00;'>Steps today: 4,235</p>
        <p style='color: #00FF00;'>Sleep quality: Good (7.5 hours)</p>
        <p style='color: #00FF00;'>Heart rate: 65 bpm (resting)</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style='text-align: center; margin-top: 30px; color: #888888;'>
    <p>Inspired by the film "Her" (2013) | Built for Google Cloud Japan AI Hackathon Vol.2</p>
</div>
""", unsafe_allow_html=True)