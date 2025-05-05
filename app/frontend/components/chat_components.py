import streamlit as st
import requests
import json
import os
from datetime import datetime

def initialize_chat():
    """Initialize chat history in session state if it doesn't exist"""
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

def display_chat():
    """Display chat interface with message history and input"""
    st.subheader("Chat with TinySwallow AI")
    
    # Initialize chat history
    initialize_chat()
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state['chat_history']:
            with st.chat_message(message['role']):
                st.markdown(message['content'])
    
    # Chat input
    user_input = st.chat_input("Ask me anything...")
    
    if user_input:
        # Add user message to history
        st.session_state['chat_history'].append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                ai_response = get_ai_response(user_input)
                st.markdown(ai_response)
        
        # Add AI response to history
        st.session_state['chat_history'].append({"role": "assistant", "content": ai_response})

def get_ai_response(user_input):
    """Get response from AI model through API"""
    api_url = "http://api:8000/chat"
    
    try:
        # Prepare request payload
        payload = {
            "message": user_input,
            "history": st.session_state['chat_history']
        }
        
        # Make API request
        response = requests.post(api_url, json=payload)
        
        if response.status_code == 200:
            return response.json()['response']
        else:
            # Fallback response if API fails
            return f"I'm sorry, I couldn't process your request. (Error {response.status_code})"
    except Exception as e:
        # Fallback for connection issues
        return f"I'm sorry, I'm having trouble connecting to my backend. Please try again in a moment. Error: {str(e)}"

def clear_chat_history():
    """Clear the chat history from session state"""
    if 'chat_history' in st.session_state:
        st.session_state['chat_history'] = []
        return True
    return False