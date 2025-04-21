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
from datetime import datetime
import subprocess

# Import streamlit_audiorecorder which is now successfully installed
from streamlit_audiorecorder import audio_recorder
AUDIO_RECORDER_AVAILABLE = True

try:
    from gtts import gTTS
    import speech_recognition as sr
    VOICE_PROCESSING_AVAILABLE = True
except ImportError:
    VOICE_PROCESSING_AVAILABLE = False
    st.warning("Voice processing libraries (gTTS/speech_recognition) are not installed. Voice output will be disabled.")

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
    if not VOICE_PROCESSING_AVAILABLE:
        return
        
    b64 = base64.b64encode(audio_data).decode()
    md = f"""
        <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

# Function to convert text to speech
def text_to_speech(text):
    if not VOICE_PROCESSING_AVAILABLE:
        return None
        
    tts = gTTS(text=text, lang='en', slow=False)
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()

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

# Function for speech recognition
def speech_to_text(audio_data):
    if not VOICE_PROCESSING_AVAILABLE:
        return None
        
    r = sr.Recognizer()
    try:
        with sr.AudioFile(audio_data) as source:
            audio = r.record(source)  # read the entire audio file
            text = r.recognize_google(audio)
            return text
    except Exception as e:
        st.error(f"Error in speech recognition: {e}")
        return None

# Function to get stock data (placeholder with random data for now)
def get_stock_data():
    # This is a placeholder. In production, you'd fetch real stock data from an API
    dates = pd.date_range(start='2025-04-01', end='2025-04-21')
    values = np.random.normal(loc=100, scale=10, size=len(dates))
    values = np.cumsum(np.random.normal(0, 1, len(dates))) + 100
    
    # Ensure values are positive
    values = np.maximum(values, 10)
    
    return pd.DataFrame({
        'Date': dates,
        'Value': values
    })

# Function to display stock chart
def display_stock_chart():
    df = get_stock_data()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date'], 
        y=df['Value'],
        mode='lines',
        name='AI Index',
        line=dict(color='#00FF00', width=2)
    ))
    
    fig.update_layout(
        title="AI Industry Stock Index",
        xaxis_title="Date",
        yaxis_title="Value",
        plot_bgcolor='#1E1E1E',
        paper_bgcolor='#1E1E1E',
        font=dict(color='#00FF00'),
    )
    
    st.plotly_chart(fig, use_container_width=True)

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
        
        # Convert AI response to speech and play it if voice processing is available
        if VOICE_PROCESSING_AVAILABLE:
            audio_data = text_to_speech(response_text.replace('[', '').replace(']', ''))
            if audio_data:
                autoplay_audio(audio_data)
        
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
col1, col2 = st.columns([3, 1])

with col1:
    # Display the terminal-like conversation interface
    display_terminal()
    
    # Text input for chat
    user_input = st.text_input("Enter your message:", key="user_input")
    
    # Voice input using streamlit_audiorecorder
    st.write("Or record your voice:")
    audio_bytes = audio_recorder(pause_threshold=2.0, sample_rate=16000)
    
    if audio_bytes:
        # Save audio to temporary file for speech recognition
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_bytes)
        
        # Convert speech to text
        if VOICE_PROCESSING_AVAILABLE:
            speech_text = speech_to_text("temp_audio.wav")
            
            if speech_text:
                chat_with_ai(speech_text)
                # Clear the input
                st.experimental_rerun()
        else:
            st.warning("Voice recording is available, but speech recognition is not. Install speech_recognition to enable this feature.")
    
    if user_input:
        chat_with_ai(user_input)
        # Clear the input box
        st.experimental_rerun()

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