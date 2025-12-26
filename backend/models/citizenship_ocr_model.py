"""
CITIZENSHIP OCR VERIFICATION MODEL
---------------------------------
- Extracts text from citizenship card using EasyOCR
- Matches OCR text with Page-1 user input
- Returns ONLY verification flags (no raw OCR text leakage)
"""

import re
from difflib import SequenceMatcher

# =========================
# OCR READER (LAZY INIT)
# =========================
_reader = None

def get_reader():
    import easyocr # Deferred import
    global _reader
    if _reader is None:
        print("[AI] Initializing EasyOCR Reader (Nepali + English)...")
        _reader = easyocr.Reader(["ne", "en"], gpu=False)
    return _reader


# =========================
# NORMALIZATION UTILITIES
# =========================

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


# =========================
# FIELD EXTRACTION
# =========================

def extract_citizenship_number(lines):
    for line in lines:
        match = re.search(r"\d{4,}", line)
        if match:
            return match.group(0)
    return None


def extract_date_of_birth(lines):
    for line in lines:
        match = re.search(
            r"(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})",
            line,
        )
        if match:
            return match.group(0)
    return None


def extract_name(lines):
    candidates = [
        line for line in lines
        if len(line) > 5 and not re.search(r"\d", line)
    ]
    return max(candidates, key=len) if candidates else None


def extract_thumbprint(image_path: str) -> bool:
    """
    Mock thumbprint detection from back image
    """
    # In a real system, use OpenCV to detect fingerprint patterns
    return True # Simulate detection


def detect_face_on_card(image_path: str) -> bool:
    """
    Verify a face exists on the ID card
    """
    try:
        # enforce_detection=True throws error if no face
        DeepFace.extract_faces(img_path=image_path, detector_backend="opencv", enforce_detection=True)
        return True
    except:
        return False


# =========================
# MAIN VERIFICATION FUNCTION
# =========================

def verify_citizenship_card(
    image_path: str,
    input_full_name: str,
    input_dob: str,
    input_citizenship_no: str,
) -> dict:
    """
    OCR + verification against Page-1 user input
    """

    # 1️⃣ OCR extraction
    ocr_texts = get_reader().readtext(image_path, detail=0)
    normalized_lines = [normalize_text(t) for t in ocr_texts]

    # 2️⃣ Extract fields from OCR
    ocr_name = extract_name(normalized_lines)
    ocr_dob = extract_date_of_birth(normalized_lines)
    ocr_cit_no = extract_citizenship_number(normalized_lines)

    # 3️⃣ Normalize user input
    input_name_norm = normalize_text(input_full_name)
    input_dob_norm = normalize_text(input_dob)
    input_cit_no_norm = normalize_text(input_citizenship_no)

    # 4️⃣ Matching rules
    name_match = (
        similarity(normalize_text(ocr_name), input_name_norm) >= 0.85
        if ocr_name else False
    )

    dob_match = (
        normalize_text(ocr_dob) == input_dob_norm
        if ocr_dob else False
    )

    cit_no_match = (
        normalize_text(ocr_cit_no) == input_cit_no_norm
        if ocr_cit_no else False
    )

    # 5️⃣ Final OCR decision
    final_status = name_match and dob_match and cit_no_match

    return {
        "name_match": name_match,
        "dob_match": dob_match,
        "citizenship_no_match": cit_no_match,
        "final_ocr_status": "PASSED" if final_status else "FAILED",
    }


# =========================
# LOCAL TEST
# =========================

if __name__ == "__main__":
    result = verify_citizenship_card(
        image_path="citizenship_front.jpg",
        input_full_name="Ram Bahadur Thapa",
        input_dob="1990-05-12",
        input_citizenship_no="12345678",
    )

    print("OCR RESULT:")
    print(result)
