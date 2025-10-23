import numpy as np
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image

model = MobileNetV2(weights="imagenet")

def detect_drug_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    decoded = decode_predictions(preds, top=3)[0]

    drug_labels = ["syringe", "bong", "pipe", "cigarette", "hookah"]
    for label, desc, prob in decoded:
        if any(d in desc.lower() for d in drug_labels):
            return {"label": "Drug-related", "confidence": float(prob), "detected": desc}

    return {"label": "Safe", "confidence": float(decoded[0][2]), "detected": decoded[0][1]}
