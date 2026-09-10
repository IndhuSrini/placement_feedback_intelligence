from nlp.cleaner import clean_message
from nlp.classifier import classify_message
from nlp.extractor import extract_information


def process_message(text: str):

    # Clean
    cleaned_text = clean_message(text)

    # Classification
    categories = classify_message(cleaned_text)

    # Information extraction
    extracted_information = extract_information(cleaned_text)

    return {
        "cleaned_text": cleaned_text,
        "categories": categories,
        "extracted_information": extracted_information
    }