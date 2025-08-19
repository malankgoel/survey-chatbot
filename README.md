# Medical Interview Assistant

A Streamlit-hosted AI tool to simulate structured diagnostic interviews. Enumerators input basic patient info, and the system asks up to 5 adaptive follow-up questions before generating a ranked list of probable diagnoses with reasoning and sources.

---

## Main code Files

- `interview.py`: Main Streamlit app logic and UI
- `utils.py`: Google Form submission + lexicon handling
- `config.py`: Constants for prompts, model, avatars, URLs, etc.

---

## Features

- Dynamic AI interviewer (asks 5 follow-up questions)
- Differential diagnosis with clinical reasoning
- Google Form integration (no OAuth needed)
- 100-word lexicon: translates technical terms into Krio or simple English
- Mobile-friendly, session-aware UI