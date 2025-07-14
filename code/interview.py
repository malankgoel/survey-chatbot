import streamlit as st
import time
from utils import (
    check_password
)
import os
import config


# Load API library
if "gpt" in config.MODEL.lower():
    api = "openai"
    from openai import OpenAI

# Set page title and icon
st.set_page_config(page_title="Interview", page_icon=config.AVATAR_INTERVIEWER)


# Initialise session state
if "interview_active" not in st.session_state:
    st.session_state.interview_active = True

# Initialise messages list in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Store start time in session state
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
    st.session_state.start_time_file_names = time.strftime(
        "%Y_%m_%d_%H_%M_%S", time.localtime(st.session_state.start_time)
    )

# Add 'Quit' button to dashboard
col1, col2 = st.columns([0.85, 0.15])
with col2:
    # If interview is active and 'Quit' button is clicked
    if st.session_state.interview_active and st.button(
        "End", help="End the interview."):
        # Set interview to inactive, display quit message, and store data
        st.session_state.interview_active = False
        quit_message = (
        "You have ended the interview." 
        "Please RELOAD THE PAGE and go to SURVEYCTO to start a new patient."
        )
        st.session_state.messages.append({"role": "assistant", "content": quit_message})


# Upon rerun, display the previous conversation (except system prompt or first message)
for message in st.session_state.messages[1:]:

    if message["role"] == "assistant":
        avatar = config.AVATAR_INTERVIEWER
    else:
        avatar = config.AVATAR_RESPONDENT
    # Only display messages without codes
    if not any(code in message["content"] for code in config.CLOSING_MESSAGES.keys()):
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# Load API client
if api == "openai":
    client = OpenAI(api_key=st.secrets["API_KEY_OPENAI"])
    api_kwargs = {"stream": True}

# API kwargs
api_kwargs["messages"] = st.session_state.messages
api_kwargs["model"] = config.MODEL
api_kwargs["max_tokens"] = config.MAX_OUTPUT_TOKENS
if config.TEMPERATURE is not None:
    api_kwargs["temperature"] = config.TEMPERATURE

# In case the interview history is still empty, pass system prompt to model, and
# generate and display its first message
if not st.session_state.messages:

    if api == "openai":

        st.session_state.messages.append(
            {"role": "system", "content": config.SYSTEM_PROMPT}
        )
        with st.chat_message("assistant", avatar=config.AVATAR_INTERVIEWER):
            stream = client.chat.completions.create(**api_kwargs)
            message_interviewer = st.write_stream(stream)

    st.session_state.messages.append(
        {"role": "assistant", "content": message_interviewer}
    )



# Main chat if interview is active
if st.session_state.interview_active:

    # Chat input and message for respondent
    if message_respondent := st.chat_input("Your message here"):
        st.session_state.messages.append(
            {"role": "user", "content": message_respondent}
        )

        # Display respondent message
        with st.chat_message("user", avatar=config.AVATAR_RESPONDENT):
            st.markdown(message_respondent)

        # Generate and display interviewer message
        with st.chat_message("assistant", avatar=config.AVATAR_INTERVIEWER):

            # Create placeholder for message in chat interface
            message_placeholder = st.empty()

            # Initialise message of interviewer
            message_interviewer = ""

            if api == "openai":

                # Stream responses
                stream = client.chat.completions.create(**api_kwargs)

                for message in stream:
                    text_delta = message.choices[0].delta.content
                    if text_delta != None:
                        message_interviewer += text_delta
                    # Start displaying message only after 5 characters to first check for codes
                    if len(message_interviewer) > 5:
                        message_placeholder.markdown(message_interviewer + "▌")
                    if any(
                        code in message_interviewer
                        for code in config.CLOSING_MESSAGES.keys()
                    ):
                        # Stop displaying the progress of the message in case of a code
                        message_placeholder.empty()
                        break

            # If no code is in the message, display and store the message
            if not any(
                code in message_interviewer for code in config.CLOSING_MESSAGES.keys()
            ):

                message_placeholder.markdown(message_interviewer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": message_interviewer}
                )


            # If code in the message, display the associated closing message instead
            # Loop over all codes
            for code in config.CLOSING_MESSAGES.keys():

                if code in message_interviewer:
                    # Store message in list of messages
                    st.session_state.messages.append(
                        {"role": "assistant", "content": message_interviewer}
                    )

                    # Set chat to inactive and display closing message
                    st.session_state.interview_active = False
                    closing_message = config.CLOSING_MESSAGES[code]
                    st.markdown(closing_message)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": closing_message}
                    )