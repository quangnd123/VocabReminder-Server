from fasttext.FastText import _FastText
import os
script_dir = os.path.dirname(os.path.abspath(__file__))

accurate_model = _FastText(os.path.join(script_dir, "lid.176.bin"))

def detect_language(text: str):
    predictions = accurate_model.predict(text=text, k=1)
    language_code = predictions[0][0].replace('__label__', '')
    confidence = predictions[1][0]
    return language_code, confidence