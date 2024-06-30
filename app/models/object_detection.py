import torch
from PIL import Image
import numpy as np
import cv2
from pathlib import Path

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

def detect_objects(image_path):
    # Perform inference
    results = model(image_path)
    return results

def crop_objects(image_path, results):
    detected_items = []
    image_pil = Image.open(image_path)
    image_np = np.array(image_pil)

    for *box, conf, cls in results.xyxy[0]:
        left, top, right, bottom = map(int, box)
        confidence = float(conf)
        class_id = int(cls)
        label = model.names[class_id]

        cropped_image_np = image_np[top:bottom, left:right]
        cropped_image_pil = Image.fromarray(cropped_image_np)

        # Save the cropped image temporarily
        cropped_image_path = 'temp.jpg'
        cropped_image_pil.save(cropped_image_path)

        detected_item = {
            'label': label,
            'confidence': confidence,
            'coordinates': (left, top, right, bottom),
            'image_path': cropped_image_path
        }
        detected_items.append(detected_item)

    return detected_items

