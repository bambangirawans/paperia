import os
import cv2
import numpy as np
import easyocr
import spacy
from langdetect import detect
from symspellpy.symspellpy import SymSpell, Verbosity
from pathlib import Path

# Initialize spaCy models
nlp_en = spacy.load("en_core_web_sm")
nlp_id = spacy.load("xx_ent_wiki_sm")
#nlp_ar = spacy.load("ar_ent_wiki_sm")

# Praproses Gambar
def preprocess_image_v1(image_path):
    # Read the image
    image = cv2.imread(image_path)
    
    # Peningkatan Kecerahan
    brightness = 50
    increased_brightness = np.where((255 - image) < brightness, 255, image + brightness)

    # Peningkatan Kontras
    contrast = 1.5
    increased_contrast = cv2.convertScaleAbs(increased_brightness, alpha=contrast, beta=0)

    # Peningkatan Ketajaman
    sharpening_kernel = np.array([[-1, -1, -1],
                                  [-1, 9, -1],
                                  [-1, -1, -1]])
    sharpened_image = cv2.filter2D(increased_contrast, -1, sharpening_kernel)

    # Pembersihan Data
    denoised_image = cv2.fastNlMeansDenoisingColored(sharpened_image, None, 10, 10, 7, 21)

    # Simpan gambar setelah praproses
    preprocessed_image_path = 'preprocessed_' + os.path.basename(image_path)
    cv2.imwrite(preprocessed_image_path, denoised_image)

    return preprocessed_image_path

def preprocess_image(image_path):
    # Load image
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Increase brightness
    alpha = 1.5 # Simple contrast control
    beta = 50    # Simple brightness control
    bright_image = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)

    # Increase contrast
    contrast_image = cv2.equalizeHist(bright_image)
    
    #Simpan gambar setelah praproses
    # Define the directory to save the cleaned images
    preprocessed_images_dir = 'preprocessed_uploads'
    # Create the directory if it doesn't exist
    os.makedirs(preprocessed_images_dir, exist_ok=True)
    # Save the cleaned image in the specified directory
    preprocessed_image_path = os.path.join(preprocessed_images_dir, 'preprocessed_' + os.path.basename(image_path))
    cv2.imwrite(preprocessed_image_path, contrast_image)

    return preprocessed_image_path
    
def clean_image(image_path):
    # Load the preprocessed image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Apply GaussianBlur to remove noise
    blurred = cv2.GaussianBlur(image, (5, 5), 0)

    # Apply thresholding to binarize image
    _, thresholded = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Apply morphological operations to further clean image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    cleaned_image = cv2.morphologyEx(thresholded, cv2.MORPH_CLOSE, kernel)
    
    # Save the cleaned image in the specified directory
    # Define the directory to save the cleaned images
    cleaned_images_dir = 'cleaned_uploads'
    # Create the directory if it doesn't exist
    os.makedirs(cleaned_images_dir, exist_ok=True)
    cleaned_image_path = os.path.join(cleaned_images_dir, 'cleaned_' + os.path.basename(image_path))
    cv2.imwrite(cleaned_image_path, cleaned_image)

    return cleaned_image_path

def extract_text_from_image(image_path):
    # Preprocess image
    preprocessed_image = preprocess_image(image_path)

    # Clean image
    cleaned_image = clean_image(preprocessed_image)

    # Extract text using OCR
    reader = easyocr.Reader(['en', 'id'])
    result = reader.readtext(cleaned_image, detail=0)
    text = ' '.join(result)
    
    return text

def scan_and_detect(image_path):
    # Perform object detection
    results = detect_objects(image_path)
    detected_items = crop_objects(image_path, results)

    for item in detected_items:
        # Perform OCR on the cropped image
        ocr_results = reader.readtext(item['image_path'])
        item['text'] = ocr_results

    return detected_items
    
# Initialize SymSpell for Indonesian
def create_symspell(max_edit_distance_dictionary, prefix_length):
    symspell = SymSpell(max_edit_distance_dictionary, prefix_length)
    dictionary_path = os.path.join(os.path.dirname(__file__), "frequency_dictionary_id.txt")
    with open(dictionary_path, 'r', encoding='utf-8') as f:
        corpus = Path(dictionary_path)
        symspell.load_dictionary(str(corpus), 0, 1)
    return symspell

symspell_id = create_symspell(2, 7)

def correct_text(text):
    try:
        language = detect(text)
    except:
        language = 'unknown'
    
    if language == 'en':
        return correct_english_text(text), 'en'
    elif language == 'id':
        return correct_indonesian_text(text), 'id'
    else:
        return text, 'unknown'

def correct_english_text(text):
    spell = SpellChecker()
    corrected_text = []
    words = text.split()
    
    for word in words:
        corrected_word = spell.correction(word)
        # Retain original casing
        if word.istitle():
            corrected_word = corrected_word.capitalize()
        elif word.isupper():
            corrected_word = corrected_word.upper()
        corrected_text.append(corrected_word)
    
    return ' '.join(corrected_text)

def correct_indonesian_text(text):
    suggestions = symspell_id.lookup_compound(text, max_edit_distance=2)
    if suggestions:
        return suggestions[0].term
    else:
        return text

def label_entities(text, language):
    if language == 'en':
        doc = nlp_en(text)
    elif language == 'id':
        doc = nlp_id(text)
    else:
        return []

    labels = []
    for ent in doc.ents:
        labels.append((ent.text, ent.label_))

    return labels
