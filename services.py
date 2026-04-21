from models import InputText

def analyze_text(data: InputText) -> dict:
    char_count = len(data.text)
    c_count = data.text.count(data.c)
    ratio = c_count / char_count if char_count > 0 else 0.0

    return {
        "input_text": data.text,
        "char_count": char_count,
        "c_count": c_count,
        "ratio": ratio
    }