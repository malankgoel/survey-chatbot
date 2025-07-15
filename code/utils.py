import requests

GOOGLE_FORM_URL = (
    "https://docs.google.com/forms/d/e/1FAIpQLSf62GcDTUDG9d23A5s5yVeNmHkGXtLrECPoPNXG5tl_vkp1XQ/formResponse"
)

FIELD_IDS = {
    "enumerator_name": "entry.636223115",
    "patient_id":      "entry.1962987405",
    # up to 6 Q&A pairs
    "q1": "entry.1682844956", "a1": "entry.1580560439",
    "q2": "entry.851565605", "a2": "entry.2141302437",
    "q3": "entry.1976065742", "a3": "entry.1857506721",
    "q4": "entry.2031961736", "a4": "entry.1035901865",
    "q5": "entry.601683888", "a5": "entry.1330155165",
    "q6": "entry.1461694892", "a6": "entry.1579162952",
    # up to 5 diagnoses
    "d1_name":      "entry.1041399290",
    "d1_prob":      "entry.1393264760",
    "d1_reasoning": "entry.52150937",
    "d1_sources":   "entry.1257601822",
    "d2_name":      "entry.1040682865",
    "d2_prob":      "entry.710098858",
    "d2_reasoning": "entry.603667358",
    "d2_sources":   "entry.201495086",
    "d3_name":      "entry.853890785",
    "d3_prob":      "entry.1326445070",
    "d3_reasoning": "entry.1923096832",
    "d3_sources":   "entry.352544246",
    "d4_name":      "entry.135241092",
    "d4_prob":      "entry.1359377000",
    "d4_reasoning": "entry.1673248795",
    "d4_sources":   "entry.2492679",
    "d5_name":      "entry.227891004",
    "d5_prob":      "entry.367523334",
    "d5_reasoning": "entry.1392807888",
    "d5_sources":   "entry.714008225",
    # summary
    "summary":      "entry.1586388785",
}

def submit_to_google_form(parsed, enumerator_name, patient_id):
    form_data = {
        FIELD_IDS["enumerator_name"]: enumerator_name,
        FIELD_IDS["patient_id"]:      patient_id,
    }

    # QA pairs (1–6)
    for i, qa in enumerate(parsed.get("qa_pairs", []), start=1):
        qk = FIELD_IDS.get(f"q{i}")
        ak = FIELD_IDS.get(f"a{i}")
        if qk: form_data[qk] = qa.get("question", "")
        if ak: form_data[ak] = qa.get("answer", "")

    # Diagnoses (1–5)
    for i, diag in enumerate(parsed.get("diagnoses", []), start=1):
        nk = FIELD_IDS.get(f"d{i}_name")
        pk = FIELD_IDS.get(f"d{i}_prob")
        rk = FIELD_IDS.get(f"d{i}_reasoning")
        sk = FIELD_IDS.get(f"d{i}_sources")
        if nk: form_data[nk] = diag.get("name", "")
        if pk: form_data[pk] = diag.get("probability", "")
        if rk: form_data[rk] = diag.get("reasoning", "")
        if sk: form_data[sk] = "; ".join(diag.get("sources", []))

    # Summary
    form_data[FIELD_IDS["summary"]] = parsed.get("summary", "")

    return requests.post(GOOGLE_FORM_URL, data=form_data)
