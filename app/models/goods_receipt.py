import os
import cv2
import easyocr
import torch
from ultralytics import YOLO

# Initialize YOLO model (assuming YOLOv8 with COCO dataset or a custom trained model)
model = YOLO('yolov8n.pt')  # Use the correct model path

# Initialize EasyOCR
reader = easyocr.Reader(['en','id'])

def extract_text_from_image_po(image_path):
    # Read the image using OpenCV
    image = cv2.imread(image_path)

    # Use EasyOCR to extract text
    result = reader.readtext(image)
    extracted_text = ' '.join([text for (_, text, _) in result])

    return extracted_text

def detect_objects_in_image(image_path):
    # Perform object detection
    results = model(image_path)
    
    # Process results
    detections = []
    for result in results.xyxy[0]:
        xmin, ymin, xmax, ymax, confidence, class_id = result
        detections.append({
            'bounding_box': [xmin.item(), ymin.item(), xmax.item(), ymax.item()],
            'confidence': confidence.item(),
            'class_id': int(class_id.item())
        })

    return detections

def verify_goods_receipt(image_path, expected_items):
    # Extract text from the image (delivery document)
    extracted_text = extract_text_from_image_po(image_path)

    # Detect objects in the image (goods)
    detected_objects = detect_objects_in_image(image_path)

    # Logic to verify extracted text against expected items
    # (This is a placeholder logic, adjust based on your requirements)
    verification_results = {
        'text_verification': extracted_text,
        'object_detection': detected_objects,
        'verification_status': 'success'  # or 'failure' based on actual verification logic
    }

    return verification_results

def process_goods_receipt(image_path, expected_items):
    try:
        verification_results = verify_goods_receipt(image_path, expected_items)
        return {
            'status': 'success',
            'data': verification_results
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
