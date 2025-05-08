import fasttext
import os
import json

CONFIDENCE_LANGUAGE_DETECTION_THRESHOLD = 0.25

script_dir = os.path.dirname(os.path.abspath(__file__))

accurate_model = fasttext.load_model(os.path.join(script_dir, "lid.176.bin"))

# Load the JSON
json_path = os.path.join(script_dir, "languages.json")
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
code2name = {entry['code']: entry['name'] for entry in data}


def detect_language(text: str) -> str:
    text = text.replace("\n", " ")  # ensure single line
    predictions = accurate_model.predict(text=text, k=1, threshold=CONFIDENCE_LANGUAGE_DETECTION_THRESHOLD)
    if not predictions[0]:
        return "unknown"
    language_code = predictions[0][0].replace('__label__', '')
    #confidence = predictions[1][0]
    return language_code


def code_to_name(code: str) -> str:
    """
    Convert a language code to its full name.
    """
    return code2name.get(code, "Unknown language")