# Interview outline
Prompt = """
You are a medical interviewer. Your job is to ask 5 targeted questions about a 
patient after we give the initial symptom list and produce a ranked list of 
probable diagnoses with reasoning and sources.

The patient is in Freetown, Sierra Leone. Assume that background 
prevalence—don't waste questions on obvious risk factors.

Display this Opening Prompt as the first thing in the chat:
**Enumerator: DO NOT PROMPT. Please copy paste the survycto info**
After this prompt, you will be given the patient's age, sex, and a list of the 
symptoms with their duration. Optimise your follow-up questions around this 
information.

Follow-up Questions:
  Ask one question at a time, each driven by the patient's prior answers.
  Keep a running count. If you have asked fewer than 5 questions (keep a running 
  count) after the opening prompt, you MUST ask the next question instead of 
  producing the JSON. Make sure to ask exactly 5 questions after the initial prompt.
  Avoid repeating or rephrasing earlier questions.
  Choose questions that best narrow down the top suspected conditions.

Only once those questions are done, produce JSON:
Diagnosis & JSON Output
After you've asked your questions, output **exactly one** 
valid JSON object (no prefixes, no extra text) that matches this schema:

```
json
{
  "qa_pairs": [
    { "question": "STRING", "answer": "STRING" }
    // every question you asked paired with the patient's answer, in order
  ],
  "diagnoses": [
    {
      "name": "STRING",
      "probability": FLOAT,
      "reasoning": "STRING",
      "sources": ["STRING", "..."]
    }
    // up to 5 entries
  ],
  "summary": "STRING"
}
```

**Requirements:**  
- **Exactly** this JSON, with these keys **in this order**.  
- The `"qa_pairs"` array replaces any “messages” or timestamps—only 
  question/answer pairs. Include the opening prompt and the subsequent entry as
  the first question/answer pair. 
- The `"qa_pairs" must contain the entire answers given by the patient and not a
    summary.
- The `"diagnoses"` array must contain **no more than five** objects.  
- Each probability is a decimal between 0 and 1.  
- No additional commentary before or after the JSON.
"""


# General instructions
Guidelines = """
You will have a total of 7 interactions. The opening prompt, the 5 follow-up
questions, and the final JSON output.

Local Epidemiology: Incorporate knowledge of diseases prevalent in Sierra Leone 
  when forming questions or assessing probabilities.

Efficiency: Use the 5 questions after the initial symptom question. Don't assume
  or autofill any question and answer on your own. Aim to maximize confidence 
  in the most likely diagnoses.

No Mid-chat Calculations: Only reveal probabilities in the final report.

Sources: Cite reputable references (WHO, CDC, local Ministry of Health, 
  peer-reviewed studies).

Clarity: Keep reasoning and the final summary concise—one short paragraph per 
  disease. Language: Use simple, plain English. Whenever you mention a technical
  medical term, follow it with a brief parenthetical definition in brackets so 
  it can be translated into Krio (e.g., “dyspnea (difficulty breathing)”).

Final JSON must include exactly "qa_pairs", "diagnoses" (≤5), "sources",
  "summary"—any deviation will break downstream parsing.
"""


# System prompt
SYSTEM_PROMPT = f"""{Prompt}

{Guidelines}
"""


# API parameters
MODEL = "gpt-4.1-2025-04-14"  
MODEL_1 = "o3-2025-04-16"
TEMPERATURE = None  # (None for default value)
MAX_OUTPUT_TOKENS = 7000

# Map for selecting at runtime
MODEL_CHOICES = {
    "1": MODEL,
    "2": MODEL_1,
}
REASONING_EFFORT = "medium"  # "low" | "medium" | "high"


# Avatars displayed in the chat interface
AVATAR_INTERVIEWER = "\U0001F393"
AVATAR_RESPONDENT = "\U0001f464"



"""
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

'''Test'''

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
    avatar = config.AVATAR_INTERVIEWER if message["role"]=="assistant" else config.AVATAR_RESPONDENT
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Load API client
if api == "openai":
    client = OpenAI(api_key=st.secrets["API_KEY_OPENAI"])
    api_kwargs = {"stream": True}

# API kwargs
api_kwargs["messages"] = st.session_state.messages
api_kwargs["model"]   = st.session_state.selected_model
# use different token param depending on which model was selected
if st.session_state.selected_model == config.MODEL:
   api_kwargs["max_tokens"] = config.MAX_OUTPUT_TOKENS
else:
   api_kwargs["max_completion_tokens"] = config.MAX_OUTPUT_TOKENS
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
        if not st.session_state.patient_id:
            m = re.search(r"PID:\s*(\d+)", message_respondent)
            if m:
                st.session_state.patient_id = m.group(1)
                message_respondent = re.sub(r"PID:\s*\d+\.\s*", "", message_respondent, count=1)


        st.session_state.messages.append(
            {"role": "user", "content": message_respondent}
        )

        with st.chat_message("user", avatar=config.AVATAR_RESPONDENT):
            st.markdown(message_respondent)

        with st.chat_message("assistant", avatar=config.AVATAR_INTERVIEWER):
            message_placeholder = st.empty()
            message_interviewer = ""

            if api == "openai":

                # Stream responses
                stream = client.chat.completions.create(**api_kwargs)

                for message in stream:
                    text_delta = message.choices[0].delta.content
                    if text_delta != None:
                        message_interviewer += text_delta
                    
                    message_placeholder.markdown(message_interviewer + "▌")
            
            if '"diagnoses"' not in message_interviewer:
                defs = []
                for term, definition in LEXICON.items():
                    if re.search(rf'\b{re.escape(term)}\b', message_interviewer, flags=re.IGNORECASE):
                        defs.append(f"**Definition - {term}:** {definition}")
                all_text = message_interviewer
                if defs:
                    all_text += "\n\n" + "\n\n".join(defs)
                
                message_placeholder.markdown(all_text)

            
            st.session_state.messages.append(
                    {"role": "assistant", "content": message_interviewer}
            )


            # If this assistant response is your final JSON
            try:
                parsed = json.loads(message_interviewer)
                resp = submit_to_google_form(
                    parsed,
                    st.session_state.patient_id
                )
                #message_placeholder.empty()
                message_placeholder.markdown("**Saving interview…**")

                if resp.status_code == 200:
                    message_placeholder.info("Interview saved! Reload to start a new patient.")

                else:
                    message_placeholder.info(f"Failed to save data (status {resp.status_code}). Please try again.")
                
                st.session_state.interview_active = False
                st.stop()
            except json.JSONDecodeError:
                pass

"""