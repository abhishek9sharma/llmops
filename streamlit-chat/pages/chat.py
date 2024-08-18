import streamlit as st

st.title("ChatGPT-like clone")
from utils import *

if __name__ == "__main__":
    setup_chat(endpoint="http://ollama-backend:11434/v1", model_name="codellama:7b")
