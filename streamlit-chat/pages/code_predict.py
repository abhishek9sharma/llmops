import streamlit as st
import requests


def get_prediction_from_llm(question, model):

    url = "http://ollama-backend:11434/api/generate"

    payload = {"model": model, "prompt": f"{question}"}
    headers = {"content-type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    print(get_context(question))
    return response


def get_context(question):
    response = requests.post(
        "http://fastapi-backend:8001/embedding/generate-embedding",
        json={"collection_name": "code", "query": question},
    )
    return response.json()


def main():
    st.title("Streamlit Chat Frontend")

    # Input field for messages
    input_code = st.text_input("Code", "")
    model = st.text_input("model")
    if input_code and model:
        response = get_prediction_from_llm(input_code, model)
        st.write(response)


if __name__ == "__main__":
    main()
