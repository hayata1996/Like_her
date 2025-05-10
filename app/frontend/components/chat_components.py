import streamlit as st
import requests
import os
from datetime import datetime

# APIのURLを環境変数から取得するか、デフォルト値を使用
API_URL = os.environ.get("API_URL", "http://api:8080")

def initialize_conversation():
    """Initialize session state for conversation history"""
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []

    if 'system_message' not in st.session_state:
        current_time = datetime.now().strftime("%H:%M:%S")
        greeting = f"[{current_time}] System initialized. Hello, I'm your personal AI assistant."
        st.session_state.system_message = greeting
        st.session_state.conversation.append({"role": "assistant", "content": greeting})

def chat_with_ai(user_input):
    """Process user input and get AI response"""
    if not user_input:
        return
    
    # Add user message to conversation history
    st.session_state.conversation.append({"role": "user", "content": user_input})
    
    try:
        # Call API for AI response
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "message": user_input,
                "history": st.session_state.conversation[:-1]  # Exclude the latest user message
            }
        )
        
        if response.status_code == 200:
            ai_response = response.json().get("response", "Sorry, I couldn't process that.")
        else:
            ai_response = f"Error: Received status code {response.status_code} from API"
    except Exception as e:
        ai_response = f"Error communicating with API: {str(e)}"
    
    # Add AI response to conversation history
    st.session_state.conversation.append({"role": "assistant", "content": ai_response})
    
    return ai_response

def display_chat():
    """Display chat interface with message history and input"""
    st.subheader("Chat with TinySwallow AI")
    
    # Initialize conversation
    initialize_conversation()
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.conversation:
            with st.chat_message(message['role']):
                st.markdown(message['content'])
    
    # Chat input
    user_input = st.chat_input("Ask me anything...")
    
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                ai_response = chat_with_ai(user_input)
                st.markdown(ai_response)

def clear_conversation():
    """Clear the conversation history from session state"""
    if 'conversation' in st.session_state:
        st.session_state.conversation = []
        return True
    return False