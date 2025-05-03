import os

import streamlit as st
from litellm import completion


def get_available_models():
    # Read models from environment variables (OPEN_AI_MODELS, DEEPSEEK_MODELS, etc.)
    models = []
    for var, value in os.environ.items():
        if var.endswith("_MODELS"):
            models.extend(value.split(","))
    return [model.strip() for model in models]




def get_llm_config():
    """
    Dynamically load available backend configurations from environment variables.
    Now also handles model-to-backend mapping based on model prefixes.
    """
    configs = {}
    for var, value in os.environ.items():
        if var.endswith("_ENDPOINT"):
            backend = var[:-9].lower()  # remove '_ENDPOINT'
            configs.setdefault(backend, {})["endpoint"] = value
        elif var.endswith("_API_KEY"):
            backend = var[:-8].lower()  # remove '_API_KEY'
            configs.setdefault(backend, {})["api_key"] = value

    # Add model-to-backend mapping
    for var, value in os.environ.items():
        if var.endswith("_MODELS"):
            backend = var[:-7].lower()  # remove '_MODELS'
            if backend in configs:
                for model in value.split(","):
                    configs[model.strip()] = configs[backend]
    return configs

def chat_with_model(model, message, history):
    """
    Modified to automatically select backend based on model name.
    """
    configs = get_llm_config()
    current_config = configs.get(model)
    if not current_config:
        raise ValueError(f"No configuration found for model: {model}")
    response = completion(
        api_base=current_config["endpoint"],
        api_key=current_config["api_key"],
        model=model,
        messages=[{"role": "user", "content": message}],
        stream=True,
    )
    for chunk in response:
        yield chunk.choices[0].delta.content


    #return response.get("content", response)

# Sidebar: Model selection
st.sidebar.title("Settings")
available_models = get_available_models()
selected_model = st.sidebar.selectbox("Choose a model", available_models)

# Main Chat Area
st.title("AI Chat Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Get streaming response
        response = chat_with_model(selected_model, prompt, st.session_state.messages)
        
        # Stream the response
        for chunk in response:
            if chunk is not None:
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")
            
        # Remove the cursor and show final response
        response_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})