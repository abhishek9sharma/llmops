import streamlit as st
import requests
import json
from typing import Dict, List, Optional
import openai

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

def send_chat_request(messages: List[Dict], 
                      endpoint:str, api_key: str, 
                      model:str,
                      guards_enabled: bool, 
                      selected_guards: List[str]) -> Optional[str]:
    """Send chat request to the API with optional guards"""
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 1000
    }
    
    # Add guard configuration if enabled
    if guards_enabled and selected_guards:
        payload["safety_guards"] = selected_guards
    
    try:
        client = openai.OpenAI(
            api_key=st.session_state.api_key,
            base_url=endpoint  # If using a custom endpoint
        )
        
        response_stream = client.chat.completions.create(
            model=model_name,
            messages=[{"role": m["role"], "content": m["content"]} for m in messages],
            timeout=120,
            stream=True
        )
        #st.write(response_stream)
        return response_stream
    except openai.APIError as e:
        st.error(f"API request failed: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

# App layout
st.title("🤖 AI Chat Assistant with Guardrails Functionality")
st.markdown("Chat with an OpenAI-compliant API endpoint")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")

    # Configuration section
    st.sidebar.header("API Configuration")
    
    endpoint = st.sidebar.text_input(
        "API Endpoint", 
        value="http://ollama-service:11434/v1/",
        help="The API endpoint for the chat completions"
    )
    
    api_key = st.sidebar.text_input(
        "API Key", 
        value="ollama",
        type="password",
        help="API key for authentication"
    )
    
    model_name = st.sidebar.text_input(
        "Model Name", 
        value="llama3.1:8b",
        help="The model to use for chat completions"
    )
  
    st.session_state.api_key = api_key
    st.session_state.model = model_name
    
    # Guard settings
    st.header("Safety Guards")
    guards_enabled = st.checkbox("Enable Safety Guards", value=False)
    
    if guards_enabled:
        selected_guards = st.multiselect(
            "Select Guard Types",
            ["PII", "Toxic"],
            default=["PII", "Toxic"],
            help="PII: Personal Identifiable Information, Toxic: Harmful content detection"
        )
    else:
        selected_guards = []
    
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
st.header("Chat")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        if not st.session_state.api_key:
            st.error("Please enter your API key in the sidebar")
        else:
            with st.spinner("Thinking..."):
                stream = send_chat_request(
                    st.session_state.messages,
                    endpoint,
                    st.session_state.api_key,
                    model_name,
                    guards_enabled,
                    selected_guards
                )
                response = st.write_stream(stream)
                if response:
                    #st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    st.error("Failed to get response from API")

# Status information
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Chat History:** {len(st.session_state.messages)} messages")
if guards_enabled:
    st.sidebar.success(f"Guards enabled: {', '.join(selected_guards)}")
else:
    st.sidebar.warning("Safety guards disabled")