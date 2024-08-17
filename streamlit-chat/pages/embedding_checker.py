# Placeholder Streamlit App

import uuid
from typing import Tuple

import requests
import streamlit as st


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


def upload_file():
    uploaded_file = st.file_uploader("Choose a code file", type=["py", "java"])
    if uploaded_file is not None:
        return uploaded_file.read().decode("utf-8")


def generate_embedding(code_content):
    # Assuming the FastAPI endpoint is running locally on port 8000
    response = requests.post(
        "http://fastapi-backend:8001/embedding/generate-embedding",
        json={"code": code_content},
    )
    return response.json()


def send_message_to_backend(sender, message):
    """
    Send a message to the FastAPI backend.
    """
    url = "http://fastapi-backend:8001/messages/"  # Adjust the URL as necessary
    headers = {"Content-Type": "application/json"}
    data = {"sender": sender, "message": message}
    response = requests.post(url, json=data, headers=headers)
    return response.json()


def fetch_messages_from_backend():
    """
    Fetch messages from the FastAPI backend.
    """
    url = "http://fastapi-backend:8001/messages/"
    response = requests.get(url)
    return response.json()


def main():
    st.title("Streamlit Chat Frontend")

    # # Input field for messages
    # new_message_sender = st.text_input("Your Name:", "")
    # new_message_text = st.text_input("Enter your message:")

    # Button to submit the message
    if st.button("Submit"):
        if new_message_text.strip():  # Check if the message is not empty
            response = send_message_to_backend(new_message_sender, new_message_text)
            st.success(f"Message sent successfully: {response}")
            # Optionally, refresh the messages display after sending a new message
            messages = fetch_messages_from_backend()
            for message in messages:
                st.write(f"{message['sender']}: {message['message']}")

    uploaded_code = upload_file()
    if st.button("Generate Embedding"):
        if uploaded_code is not None:
            st.write(uploaded_code)
            embedding = generate_embedding(uploaded_code)
            st.write(embedding)
        else:
            st.write("Please upload a code file.")

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


if __name__ == "__main__":
    main()
