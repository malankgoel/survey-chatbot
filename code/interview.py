import streamlit as st
import time
import config
from utils import submit_to_google_form, LEXICON
import json
import re
from openai import OpenAI

api = "openai"

# Set page title and icon
st.set_page_config(page_title="Interview", page_icon=config.AVATAR_INTERVIEWER)
if "interview_active" not in st.session_state:
    st.session_state.interview_active = True

if "disclaimer_accepted" not in st.session_state:
    st.session_state.disclaimer_accepted = False

# --- Disclaimer Gate ---
if not st.session_state.disclaimer_accepted:
    st.header("Before you proceed")
    st.markdown(config.DISCLAIMER_MD)

    c1, c2 = st.columns([1, 1])
    agree = c1.button("I agree", type="primary")
    disagree = c2.button("I do not agree")

    if agree:
        st.session_state.disclaimer_accepted = True
        st.rerun()  # start the app flow normally
    elif disagree:
        st.info("You can close this page or refresh if you change your mind.")
        st.stop()   # do not render the rest of the app

    # If neither button pressed yet, halt rendering of the rest of the page
    st.stop()
# --- End Disclaimer Gate ---


if "interaction_step" not in st.session_state:
    st.session_state.interaction_step = 0

if "messages" not in st.session_state:
    st.session_state.messages = []

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
    st.session_state.start_time_file_names = time.strftime(
        "%Y_%m_%d_%H_%M_%S", time.localtime(st.session_state.start_time)
    )

#st.markdown(config.HIDE_MOBILE_BUTTONS_CSS, unsafe_allow_html=True)

if "selected_model" not in st.session_state:
        st.session_state.selected_model = config.MODEL
        st.session_state.reasoning_effort = config.REASONING_EFFORT

if "patient_id" not in st.session_state:
    st.session_state.patient_id = ""

if st.session_state.disclaimer_accepted:
    for message in st.session_state.messages[1:]:
        avatar = config.AVATAR_INTERVIEWER if message["role"] == "assistant" else config.AVATAR_RESPONDENT
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])


# Load API client
if api == "openai":
    client = OpenAI(api_key=st.secrets["API_KEY_OPENAI"])
    api_kwargs = {"stream": True}



# API kwargs
api_kwargs["messages"] = st.session_state.messages
api_kwargs["model"] = st.session_state.selected_model  # o3
api_kwargs["max_completion_tokens"] = config.MAX_OUTPUT_TOKENS
if config.TEMPERATURE is not None:
    api_kwargs["temperature"] = config.TEMPERATURE
api_kwargs["reasoning_effort"] = config.REASONING_EFFORT


# Initial system prompt & first interviewer message
if st.session_state.disclaimer_accepted and not st.session_state.messages:
    st.session_state.messages.append({"role": "system", "content": config.SYSTEM_PROMPT})
    with st.chat_message("assistant", avatar=config.AVATAR_INTERVIEWER):
        stream = client.chat.completions.create(**api_kwargs)
        message_interviewer = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": message_interviewer})
    st.session_state.interaction_step = 1


# Main chat
if st.session_state.disclaimer_accepted and st.session_state.interview_active:
    if message_respondent := st.chat_input("Your message here"):
        if not st.session_state.patient_id:
            m = re.search(r"PID:\s*(\d+)", message_respondent)
            if m:
                st.session_state.patient_id = m.group(1)
                message_respondent = re.sub(r"PID:\s*\d+\.?\s*", "", message_respondent, count=1)

        st.session_state.messages.append({"role": "user", "content": message_respondent})
        with st.chat_message("user", avatar=config.AVATAR_RESPONDENT):
            st.markdown(message_respondent)

        with st.chat_message("assistant", avatar=config.AVATAR_INTERVIEWER):
            message_placeholder = st.empty()
            message_interviewer = ""
            next_step = st.session_state.interaction_step + 1

            stream = client.chat.completions.create(**api_kwargs)
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                message_interviewer += delta
                if next_step < 7:
                    annotated = message_interviewer
                    for term, definition in LEXICON.items():
                        pattern = re.compile(rf'\b{re.escape(term)}\b', flags=re.IGNORECASE)
                        annotated = pattern.sub(lambda m: f"{m.group(0)} ({definition})", annotated)
                    message_placeholder.markdown(annotated)

            if next_step < 7:
                pass
            else:
                message_placeholder.empty()
                try:
                    clean = message_interviewer.strip()
                    parsed = json.loads(clean)
                    parsed["model_info"] = f"5, {config.REASONING_EFFORT}"
                    resp = submit_to_google_form(parsed, st.session_state.patient_id)
                    if resp.status_code == 200:
                        st.success("Interview saved! Reload to start a new patient.")
                    else:
                        st.error(f"Failed to save data (status {resp.status_code}).")
                except json.JSONDecodeError:
                    st.error("Unexpected format; interview not saved.")
                    st.write("DEBUG RAW OUTPUT:", message_interviewer)
                st.session_state.interview_active = False

            st.session_state.messages.append({"role": "assistant", "content": message_interviewer})
            st.session_state.interaction_step = next_step