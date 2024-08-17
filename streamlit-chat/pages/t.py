import streamlit as st


def main():
    st.title("Streamlit Chat Frontend")

    # Input field for messages
    new_message_sender = st.text_input("Your Name:", "")
    # #new_message_text = st.text_input("Enter your message:")


if __name__ == "__main__":
    main()
