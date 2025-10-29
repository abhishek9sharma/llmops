import uuid
from typing import Tuple

import requests
import streamlit as st
from openai import OpenAI

OLLAMA_ENDPOINT = "http://localhost:11434"
FAST_API_BACKEND = "http://fastapi-backend:8001"
VECTOR_API_BACKEND = "http://vector-backend:8000"


def get_models():
    models = requests.get(f"{OLLAMA_ENDPOINT}/api/tags")
    model_names = [m["name"] for m in models.json()["models"]]
    return model_names


def openai_endpoint(endpoint, model_name, messages, use_context="NO"):
    # st.write(messages)
    if use_context == "YES":
        latest_message = messages[-1]["content"]
        context = query_collection(latest_message)
        context_documents = context["documents"][0]
        messages[-1]["content"] = formatted_prompt = format_question_with_context(
            latest_message, context_documents
        )
    # st.write(messages)
    client = OpenAI(base_url=endpoint, api_key="ollama")
    return client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[{"role": m["role"], "content": m["content"]} for m in messages],
        stream=True,
    )


def setup_chat(endpoint, model_name, use_context="NO"):

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = model_name

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # for message in st.session_state.messages:
    #     with st.chat_message(message["role"]):
    #         st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        # st.write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            stream = openai_endpoint(
                endpoint, model_name, st.session_state.messages, use_context
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})


def send_file_to_fastapi(content: str, document_id: str) -> Tuple[bool, str]:
    """
    Sends a file to the specified FastAPI endpoint and returns a tuple indicating success and the response message.

    Parameters:
    - file_path: Path to the file to be uploaded.
    - document_id: The UUID to be included in the URL path.

    Returns:
    A tuple containing a boolean indicating success and the response message.
    """
    # url = ff"{FAST_API_BACKEND}/update_context/request_id={document_id}"
    # with open(file_path, "rb") as file:
    #     files = {"file": ("filename.txt", file, "text/plain")}
    #     response = requests.post(url, files=files)
    # Assuming the FastAPI endpoint is running locally on port 8000
    response = requests.post(
        f"{FAST_API_BACKEND}/embedding/update_context",
        json={"contents": content, "request_id": document_id},
    )
    # return response.json()
    if response.status_code == 200:
        return True, response.json()  # ["message"]
    else:
        return False, response.text


def del_collection(collection_name):
    url = f"{VECTOR_API_BACKEND}/api/v1/collections/{collection_name}"
    st.write(f"attempted to delete {collection_name}")

    querystring = {"tenant": "default_tenant", "database": "default_database"}
    headers = {"accept": "application/json"}
    response = requests.delete(url, headers=headers, params=querystring)
    st.markdown(response.json())


def upload_file():
    uploaded_file = st.file_uploader("Choose a code file", type=["py", "java"])
    if uploaded_file is not None:
        return uploaded_file.read().decode("utf-8")


def format_question_with_context(question, documents):
    similar_snippets = ["```" + d + "```" for d in documents]
    similar_snippets_text = "\n\n".join(similar_snippets)
    formatted_prompt = f""""
                    You are a software developer. Please see the examples below\n
                    {similar_snippets_text}
                    Now answer the below question based on the above examples you have read\n
                    {question}
                    """
    return formatted_prompt


def get_prediction_from_llm(question, model):

    url = f"{OLLAMA_ENDPOINT}/api/generate"

    context = query_collection(question)
    documents = context["documents"][0]
    st.markdown(documents)
    formatted_prompt = format_question_with_context(question, documents)

    payload = {
        "model": model,
        "prompt": f"{formatted_prompt}",
        "options": {"temperature": 0, "num_predict": 20},
        "stream": False,
    }

    st.markdown(payload)
    headers = {"content-type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def query_collection(query):
    response = requests.post(
        f"{FAST_API_BACKEND}/embedding/query_collection",
        json={"collection_name": "code", "query": query},
    )
    return response.json()


def get_collection(collection_name):
    vec_api = f"{VECTOR_API_BACKEND}/api/v1/collections/{collection_name}?tenant=default_tenant&database=default_database"
    st.write(vec_api)
    info = requests.get(vec_api)
    return info.json()
