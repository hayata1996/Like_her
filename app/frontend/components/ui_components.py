import streamlit as st
from datetime import datetime
import base64

# Custom CSS for terminal-like interface
def apply_custom_css():
    if 'css_applied' not in st.session_state:
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
        st.session_state.css_applied = True

def setup_page_config():
    """Configure the Streamlit page settings"""
    st.set_page_config(
        page_title="Like Her - AI Assistant",
        page_icon="🎧",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

def initialize_session_state():
    """Initialize the session state variables"""
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []

    if 'system_message' not in st.session_state:
        current_time = datetime.now().strftime("%H:%M:%S")
        greeting = f"[{current_time}] System initialized. Hello, I'm your personal AI assistant."
        st.session_state.system_message = greeting
        st.session_state.conversation.append({"role": "assistant", "content": greeting})

def display_terminal():
    """Display terminal-like text interface for conversation"""
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

def autoplay_audio(audio_data):
    """Autoplay audio data in the browser"""
    if audio_data is None:
        return
        
    b64 = base64.b64encode(audio_data).decode()
    md = f"""
        <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

def display_footer():
    """Display the application footer"""
    st.markdown("""
    <div style='text-align: center; margin-top: 30px; color: #888888;'>
        <p>Inspired by the film "Her" (2013) | Built for Google Cloud Japan AI Hackathon Vol.2</p>
    </div>
    """, unsafe_allow_html=True)