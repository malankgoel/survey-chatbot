import requests

LEXICON = {
    'Fever': 'Wam Body',
    'Chills': 'Feel cold ',
    'Sweating': 'Sweat',
    'Headache': 'Aid hat',
    'Muscle pain': 'Muscle pain',
    'Joint pain': 'Joint pain',
    'Body weakness': 'Feel weak',
    'Fatigue': 'Taya',
    'Dizziness': 'Turn aid',
    'Nausea': 'Feel bad',
    'Vomiting': 'Vomit',
    'Diarrhea': 'Run beleh',
    'Constipation': 'Dry beleh',
    'Abdominal pain': 'Bottom beleh dae hat',
    'Stomach bloating': 'Big beleh',
    'Loss of appetite': 'Nor feel for eat',
    'Weight loss': 'Body drop',
    'Sore throat': 'Sore throat',
    'Cough': 'Cough',
    'Chest pain': 'Pain na the chest',
    'Shortness of breath': 'Breath fast fast',
    'Wheezing': 'Pull sound wae you dae breath',
    'Nasal congestion': 'Nose block',
    'Runny nose': 'Nose dae run',
    'Sneezing': 'Sneezing',
    'Ear pain': 'yeas dae hat',
    'Hearing loss': 'Nor dae yeri',
    'Eye pain': 'Yie hat',
    'Eye redness': 'Red yie',
    'Blurred vision': 'Nor dae see clear',
    'Swollen eyelids': 'Swell yie',
    'Toothache': 'Teet hat',
    'Mouth sores': 'Wound na mot',
    'Swollen gums': 'Swell gum',
    'Neck pain': 'Neck pain',
    'Stiff neck': 'Neck dae stiff',
    'Back pain': 'Back pain',
    'Skin rash': 'Skin rash',
    'Itching': 'Scrach scrach',
    'Dry skin': 'Dry skin',
    'Peeling skin': 'Body dae peel',
    'Swelling under the skin': 'Swelling',
    'Lumps on the body': 'Bump bump',
    'Sores on the skin': 'Wound na the body',
    'Ulcers on legs or feet': 'so foot',
    'Burning sensation on skin': 'The body dae burn',
    'Tingling in hands or feet': 'Hand dae bet bet',
    'Numbness': 'Loss feeling',
    'Weakness in arms or legs': 'Weak hand or leg',
    'Tremors': 'Shake shake',
    'Loss of balance': 'Turn aid',
    'Confusion': 'Confusion',
    'Difficulty concentrating': 'Hat for focus',
    'Anxiety': 'Wori',
    'Irritability': 'Vex',
    'Depression': 'Pwel hat',
    'Insomnia': 'Nor able sleep',
    'Night sweats': 'Sweat too mus pa sleep',
    'Frequent urination': 'Piss fast fast',
    'Painful urination': 'Feel pain wae you dae piss',
    'Blood in urine': 'Piss blood',
    'Urine with strong smell': 'Piss get strong smell',
    'Bedwetting': 'piss na baid (bed)',
    'Vaginal discharge': 'Discharge from woman private part',
    'Genital itching': 'Crach Crach na woman private part ',
    'Genital sores': 'Sor na man or woman private part',
    'Swelling in groin area': 'Grin na the leg',
    'Swollen lymph nodes (neck/armpit/groin)': 'Bump bump na (neck/under hand)',
    'Bleeding gums': 'Blood the comot na the gum',
    'Nosebleeds': 'Nose the pull blood',
    'Easy bruising': 'Bruise',
    'Prolonged bleeding after injury': 'Blood nor dae stop for comot',
    'Palpitations': 'Breath heavy',
    'Fainting': 'Nor able do natin',
    'Pale skin': 'The body oale',
    'Yellowing of eyes': 'Yie yellow',
    'Swollen hands or feet': 'Swell hand or foot',
    'Cold hands or feet': 'Cold hand or foot',
    'Heat intolerance': 'Feel hot',
    'Sensitivity to light': 'Light dae affect the yie',
    'Severe thirst': 'Dae thirsty too mus',
    'Dry mouth': 'The mot dae dry',
    'Bad breath': 'Smell mot',
    'Hair loss': 'the hair dae rut rut',
    'Brittle nails': 'The nails den nor strong or nor hat for broke ',
    'Cracks in corners of mouth': 'Lassie or mot don pull fever',
    'Difficulty breathing when lying down': 'Nor able breath wae you laydom',
    'Swollen face': 'Swell face',
    'Hoarseness': 'Voice cut',
    'Swollen tongue': 'Swell tongue',
    'Bitter taste in mouth': 'Mot better',
    'Difficulty passing stool': 'Nor able toilet ',
    'Worms in stool': 'The toilet get wor worm',
    'Abdominal swelling (ascites)': '',
    'Vomiting blood': 'Vomit blood',
    'Blood in stool': 'Toilet blood',
    'something moving under skin': 'Feel lek some tine dae waka na the body',
    'General body pain': 'Pain all over d body',
    'Extreme tiredness after small activity': 'Taya quick after small wok',
    'swallow': 'Hat for swella',
}


GOOGLE_FORM_URL = (
    "https://docs.google.com/forms/d/e/1FAIpQLSf62GcDTUDG9d23A5s5yVeNmHkGXtLrECPoPNXG5tl_vkp1XQ/formResponse"
)

FIELD_IDS = {
    "model_info":   "entry.635504491",
    "patient_id":      "entry.1962987405",
    "q1": "entry.1682844956", "a1": "entry.1580560439",
    "q2": "entry.851565605", "a2": "entry.2141302437",
    "q3": "entry.1976065742", "a3": "entry.1857506721",
    "q4": "entry.2031961736", "a4": "entry.1035901865",
    "q5": "entry.601683888", "a5": "entry.1330155165",
    "q6": "entry.1461694892", "a6": "entry.1579162952",
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
    "summary":      "entry.1586388785",
}

def submit_to_google_form(parsed, patient_id):
    form_data = {
        FIELD_IDS["patient_id"]:      patient_id,
    }

    for i, qa in enumerate(parsed.get("qa_pairs", []), start=1):
        qk = FIELD_IDS.get(f"q{i}")
        ak = FIELD_IDS.get(f"a{i}")
        if qk: form_data[qk] = qa.get("question", "")
        if ak: form_data[ak] = qa.get("answer", "")

    for i, diag in enumerate(parsed.get("diagnoses", []), start=1):
        nk = FIELD_IDS.get(f"d{i}_name")
        pk = FIELD_IDS.get(f"d{i}_prob")
        rk = FIELD_IDS.get(f"d{i}_reasoning")
        sk = FIELD_IDS.get(f"d{i}_sources")
        if nk: form_data[nk] = diag.get("name", "")
        if pk: form_data[pk] = diag.get("probability", "")
        if rk: form_data[rk] = diag.get("reasoning", "")
        if sk: form_data[sk] = "; ".join(diag.get("sources", []))

    form_data[FIELD_IDS["summary"]] = parsed.get("summary", "")
    form_data[FIELD_IDS["model_info"]] = parsed.get("model_info", "")

    return requests.post(GOOGLE_FORM_URL, data=form_data)
