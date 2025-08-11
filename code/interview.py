import streamlit as st
import time
import config
from utils import submit_to_google_form, LEXICON
import json
import re
from openai import OpenAI

# Load API library
api = "openai"

# Set page title and icon
st.set_page_config(page_title="Interview", page_icon=config.AVATAR_INTERVIEWER)
# Initialise session state
if "interview_active" not in st.session_state:
    st.session_state.interview_active = True

if "interaction_step" not in st.session_state:
    st.session_state.interaction_step = 0


# Initialise messages list in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Store start time in session state
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
    st.session_state.start_time_file_names = time.strftime(
        "%Y_%m_%d_%H_%M_%S", time.localtime(st.session_state.start_time)
    )

# Prompt which model to use, then hold execution until confirmed
if "selected_model" not in st.session_state:
    choice = st.radio(
        "Choose model:",
        ("1", "2"),
        format_func=lambda x: f"{x}: {'GPT-4.1' if x=='1' else 'o3'}",
    )
    if st.button("Start Interview"):
        st.session_state.selected_model = config.MODEL_CHOICES[choice]
    st.stop()

# ─── Reasoning Effort picker ───
if (
    st.session_state.selected_model == config.MODEL_CHOICES["2"]
    and "reasoning_effort" not in st.session_state
):
    effort_choice = st.radio(
        "Choose reasoning effort:",
        ("low", "medium", "high"),
        index=1,
        format_func=lambda x: x.capitalize(),
    )
    if st.button("Confirm Effort Level"):
        st.session_state.reasoning_effort = effort_choice
    st.stop()


if "patient_id" not in st.session_state:
    st.session_state.patient_id = ""

# Add 'Quit' button to dashboard
col1, col2 = st.columns([0.85, 0.15])
with col2:
    if st.session_state.interview_active and st.button(
        "End", help="End the interview."):
        st.session_state.interview_active = False
        quit_message = (
            "You have ended the interview.\n"
            "Please RELOAD THE PAGE and go to SURVEYCTO to start a new patient."
        )
        st.session_state.messages.append({"role": "assistant", "content": quit_message})
        st.warning(quit_message)

# Upon rerun, display the previous conversation (except system prompt or first message)
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
api_kwargs["model"] = st.session_state.selected_model
if st.session_state.selected_model == config.MODEL:
    api_kwargs["max_tokens"] = config.MAX_OUTPUT_TOKENS
else:
    api_kwargs["max_completion_tokens"] = config.MAX_OUTPUT_TOKENS
if config.TEMPERATURE is not None:
    api_kwargs["temperature"] = config.TEMPERATURE

if st.session_state.selected_model == config.MODEL_CHOICES["2"]:
    api_kwargs["reasoning_effort"] = st.session_state.reasoning_effort

# Initial system prompt & first interviewer message
if not st.session_state.messages:
    # add system prompt
    st.session_state.messages.append({"role": "system", "content": config.SYSTEM_PROMPT})
    with st.chat_message("assistant", avatar=config.AVATAR_INTERVIEWER):
        # stream first question
        stream = client.chat.completions.create(**api_kwargs)
        message_interviewer = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": message_interviewer})
    # count as first interaction
    st.session_state.interaction_step = 1

# Main chat if interview is active
if st.session_state.interview_active:
    if message_respondent := st.chat_input("Your message here"):
        # extract patient_id if missing
        if not st.session_state.patient_id:
            m = re.search(r"PID:\s*(\d+)", message_respondent)
            if m:
                st.session_state.patient_id = m.group(1)
                message_respondent = re.sub(r"PID:\s*\d+\.?\s*", "", message_respondent, count=1)

        # record user message
        st.session_state.messages.append({"role": "user", "content": message_respondent})
        with st.chat_message("user", avatar=config.AVATAR_RESPONDENT):
            st.markdown(message_respondent)

        # assistant response
        with st.chat_message("assistant", avatar=config.AVATAR_INTERVIEWER):
            message_placeholder = st.empty()
            message_interviewer = ""
            next_step = st.session_state.interaction_step + 1

            # stream content but only display for steps 1–6
            # stream the model’s reply
            stream = client.chat.completions.create(**api_kwargs)
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                message_interviewer += delta
                # only render text + definitions for steps 1–6
                if next_step < 7:
                    # annotate each technical term inline, e.g. "foo (definition of foo)"
                    annotated = message_interviewer
                    for term, definition in LEXICON.items():
                        pattern = re.compile(rf'\b{re.escape(term)}\b', flags=re.IGNORECASE)
                        annotated = pattern.sub(lambda m: f"{m.group(0)} ({definition})", annotated)
                    message_placeholder.markdown(annotated)

            # after streaming completes:
            if next_step < 7:
                pass
            else:
                # Step 7: hide JSON, submit, then stop so input vanishes
                message_placeholder.empty()
                try:
                    clean = message_interviewer.strip()
                    parsed = json.loads(clean)
                    if st.session_state.selected_model == config.MODEL_CHOICES["2"]:
                        parsed["model_info"] = f"o3, {st.session_state.reasoning_effort}"
                    else:
                        parsed["model_info"] = "4.1"
                    resp = submit_to_google_form(parsed, st.session_state.patient_id)
                    if resp.status_code == 200:
                        st.success("Interview saved! Reload to start a new patient.")
                    else:
                        st.error(f"Failed to save data (status {resp.status_code}).")
                except json.JSONDecodeError:
                    st.error("Unexpected format; interview not saved.")
                    st.write("DEBUG RAW OUTPUT:", message_interviewer)
                st.session_state.interview_active = False

            # save assistant message & increment step
            st.session_state.messages.append({"role": "assistant", "content": message_interviewer})
            st.session_state.interaction_step = next_step