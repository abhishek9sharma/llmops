import streamlit as st
import requests
import uuid
from typing import Tuple


def send_file_to_fastapi(content: str, document_id: str) -> Tuple[bool, str]:
    """
    Sends a file to the specified FastAPI endpoint and returns a tuple indicating success and the response message.

    Parameters:
    - file_path: Path to the file to be uploaded.
    - document_id: The UUID to be included in the URL path.

    Returns:
    A tuple containing a boolean indicating success and the response message.
    """
    # url = f"http://fastapi-backend:8001/update_context/request_id={document_id}"
    # with open(file_path, "rb") as file:
    #     files = {"file": ("filename.txt", file, "text/plain")}
    #     response = requests.post(url, files=files)
    # Assuming the FastAPI endpoint is running locally on port 8000
    response = requests.post(
        f"http://fastapi-backend:8001/embedding/update_context",
        json={"contents": content, "request_id": document_id},
    )
    # return response.json()
    if response.status_code == 200:
        return True, response.json()  # ["message"]
    else:
        return False, response.text


def del_collection(collection_name):
    url = "http://vector-backend:8000/api/v1/collections/{collection_name}"
    st.write(f"attempted to delete {collection_name}")

    querystring = {"tenant": "default_tenant", "database": "default_database"}
    headers = {"accept": "application/json"}
    response = requests.delete(url, headers=headers, params=querystring)
    st.markdown(response.json())


def upload_file():
    uploaded_file = st.file_uploader("Choose a code file", type=["py", "java"])
    if uploaded_file is not None:
        return uploaded_file.read().decode("utf-8")


def get_prediction_from_llm(question, model):

    url = "http://ollama-backend:11434/api/generate"

    context = query_collection(question)
    documents = context["documents"][0]
    st.markdown(documents)
    similar_snippets = ["```" + d + "```" for d in documents]
    similar_snippets_text = "\n".join(similar_snippets)
    formatted_prompt = f""""
                    {similar_snippets_text}
                    Given above code snippets please answert the below question
                    {question}
                    """

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
        "http://fastapi-backend:8001/embedding/query_collection",
        json={"collection_name": "code", "query": query},
    )
    return response.json()


def get_collection(collection_name):
    info = requests.get(
        f"http://vector-backend:8000/api/v1/collections/{collection_name}?tenant=default_tenant&database=default_database"
    )
    return info.json()


def main():
    st.title("Streamlit Chat Frontend")

    # Input field for messages
    input_code = st.text_input("Code", "")
    model = st.text_input("model")
    if input_code and model:
        response = get_prediction_from_llm(input_code, model)
        st.markdown(response)

    st.title("Update Context")
    uploaded_file = st.file_uploader("Choose a file", type=["py", "java"])

    if uploaded_file is not None:
        # Generate a random UUID for demonstration purposes
        st.write(uploaded_file.getvalue())

        if st.button("Update Context"):
            # Send the file to the FastAPI endpoint
            document_id = uuid.uuid4()
            document_id_str = str(
                document_id
            )  # Replace with actual UUID generation logic
            file_content = uploaded_file.read().decode("utf-8")
            success, message = send_file_to_fastapi(file_content, document_id_str)

            if success:
                st.success(message)
            else:
                st.error(f"Failed to upload file: {message}")

    st.title("Query collection")
    query = st.text_input("query", "")
    if query:
        st.markdown(query_collection(query))

    st.title("get_collection")
    collection_to_get = st.text_input("collection to get", "")
    if collection_to_get:
        st.markdown(get_collection(collection_to_get))

    st.title("Delete collection")
    delete_collection = st.text_input("collection to delete", "")
    if delete_collection:
        del_collection(del_collection)


if __name__ == "__main__":
    main()
