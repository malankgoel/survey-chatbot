import streamlit as st
import time
import config
import json

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



# Prompt for Enumerator Name
if "enumerator_name" not in st.session_state:
    st.session_state.enumerator_name = ""

if not st.session_state.enumerator_name:
    st.session_state.enumerator_name = st.text_input(
        "Enter Enumerator Name Test:",
        value=""
    )
    if not st.session_state.enumerator_name:
        st.warning("Please enter an Enumerator Name to proceed.")
        st.stop()
else:
    st.text_input(
        "Enumerator Name:",
        value=st.session_state.enumerator_name,
        disabled=True
    )

# Prompt for PATIENT ID
if "patient_id" not in st.session_state:
    st.session_state.patient_id = ""

if not st.session_state.patient_id:
    st.session_state.patient_id = st.text_input(
        "Enter Patient ID:", 
        value=""
    )
    if not st.session_state.patient_id:
        st.warning("Please enter a Patient ID to proceed.")
        st.stop()
else:
    st.text_input(
        "Patient ID:", 
        value=st.session_state.patient_id, 
        disabled=True
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
        "You have ended the interview.\n"
        "Please RELOAD THE PAGE and go to SURVEYCTO to start a new patient."
        )
        st.session_state.messages.append({"role": "assistant", "content": quit_message})
        st.warning(quit_message)

# Upon rerun, display the previous conversation (except system prompt or first message)
for message in st.session_state.messages[1:]:
    avatar = config.AVATAR_INTERVIEWER if message["role"]=="assistant" else config.AVATAR_RESPONDENT
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

            # Stream the assistant response into a placeholder
            message_placeholder = st.empty()
            message_interviewer = ""

            # Stream and show only the running text (no raw JSON dump)
            stream = client.chat.completions.create(**api_kwargs)
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    message_interviewer += delta
                    message_placeholder.markdown(message_interviewer + "▌")

            # Finalize display
            message_placeholder.markdown(message_interviewer)
            st.session_state.messages.append(
                {"role": "assistant", "content": message_interviewer}
            )

            # Check if it's the final JSON payload
            import json
            try:
                parsed = json.loads(message_interviewer)
                if isinstance(parsed, dict) and "diagnoses" in parsed:
                    st.subheader("🔍 Final JSON Output")
                    st.json(parsed)
                    st.session_state.interview_active = False
            except json.JSONDecodeError:
                pass
