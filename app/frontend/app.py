import streamlit as st
import os
from components.ui_components import (
    setup_page_config,
    apply_custom_css,
    display_terminal
)
from components.chat_components import (
    initialize_conversation,
    chat_with_ai
)
from components.stock_components import (
    display_stock_chart,
)

# No speech processing libraries needed - using Gemini API instead
VOICE_FEATURES_ENABLED = True

# Set page configuration
setup_page_config()

# Apply custom CSS for terminal-like interface
apply_custom_css()

# Initialize session state for conversation history
initialize_conversation()

# API URL (default for local development, can be overridden by environment)
API_URL = os.environ.get("API_URL", "http://localhost:8080")


# Function to get AI news (placeholder)
def get_ai_news():
    # This is a placeholder. In production, you'd fetch real news from an API
    return [
        {
            "title": "Google DeepMind Announces New AI Architecture",
            "summary": "A breakthrough in AI architecture that improves "
                      "efficiency by 40%.",
            "date": "2025-04-20"
        },
        {
            "title": "Sakana AI Releases Expanded Version of Swallow Model",
            "summary": "Japanese AI startup Sakana AI has released Swallow 2.0 "
                      "with improved language capabilities.",
            "date": "2025-04-19"
        },
        {
            "title": "AI Regulation Framework Proposed in EU",
            "summary": "New regulations aim to ensure ethical AI development "
                      "across European markets.",
            "date": "2025-04-18"
        }
    ]


# Create the main layout
st.title("Like Her - Your Personal AI Assistant")

# Create two columns for the layout
col1, col2 = st.columns([1, 2])

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
        <div style='background-color: #1E1E1E; padding: 10px; 
             margin-bottom: 10px; border-left: 2px solid #00FF00;'>
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
    <div style='background-color: #1E1E1E; padding: 10px; 
         border-left: 2px solid #00FF00;'>
        <p style='color: #00FF00;'>Last sync: 2025-04-21 06:30 AM</p>
        <p style='color: #00FF00;'>Steps today: 4,235</p>
        <p style='color: #00FF00;'>Sleep quality: Good (7.5 hours)</p>
        <p style='color: #00FF00;'>Heart rate: 65 bpm (resting)</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style='text-align: center; margin-top: 30px; color: #888888;'>
    <p>Inspired by the film "Her" (2013) | Built for Google Cloud Japan 
       AI Hackathon Vol.2</p>
</div>
""", unsafe_allow_html=True)