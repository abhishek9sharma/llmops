# import uuid
# from typing import Tuple

# import requests
# import streamlit as st
# from utils import *
# from utils import get_models


# def main():
#     st.title("Streamlit Chat Frontend")

#     # # Input field for messages
#     # input_code = st.text_input("Code", "")
#     # model = st.text_input("model")
#     # if input_code and model:
#     #     response = get_prediction_from_llm(input_code, model)
#     #     st.markdown(response)

#     use_context = st.radio("Select an Option:", ["NO", "YES"])
#     if use_context == "YES":
#         st.title("Update Context")
#         uploaded_file = st.file_uploader("Choose a file", type=["py", "java"])

#         if uploaded_file is not None:
#             # Generate a random UUID for demonstration purposes
#             st.write(uploaded_file.getvalue())

#             if st.button("Update Context"):
#                 # Send the file to the FastAPI endpoint
#                 document_id = uuid.uuid4()
#                 document_id_str = str(
#                     document_id
#                 )  # Replace with actual UUID generation logic
#                 file_content = uploaded_file.read().decode("utf-8")
#                 success, message = send_file_to_fastapi(file_content, document_id_str)

#                 if success:
#                     st.success(message)
#                 else:
#                     st.error(f"Failed to upload file: {message}")

#         st.title("Query collection")
#         query = st.text_input("query", "")
#         if query:
#             st.markdown(query_collection(query))

#         st.title("get_collection")
#         collection_to_get = st.text_input("collection to get", "")
#         if collection_to_get:
#             st.markdown(get_collection(collection_to_get))

#         st.title("Delete collection")
#         delete_collection = st.text_input("collection to delete", "")
#         if delete_collection:
#             del_collection(del_collection)

#     available_models = get_models()
#     selected_model = st.radio("Select an Option:", available_models)
#     st.write(f"You selected: {selected_model}")

#     if selected_model:
#         setup_chat(
#             endpoint="http://ollama-backend:11434/v1",
#             model_name=selected_model,
#             use_context=use_context,
#         )


# if __name__ == "__main__":
#     main()
