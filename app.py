"""
app.py

Flask API that loads fabric_model.keras, predicts the fabric type of an uploaded image,
and looks up its sustainability category from material_database.csv.
"""

import os
import csv
import io

from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import tensorflow as tf

APP_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(APP_DIR, "fabric_model.keras")
LABELS_PATH = os.path.join(APP_DIR, "fabric_model_labels.txt")
MATERIAL_DB_PATH = os.path.join(APP_DIR, "material_database.csv")
IMG_SIZE = (224, 224)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

print("Loading fabric detection model...")
model = tf.keras.models.load_model(MODEL_PATH)
print("Model loaded successfully.")

with open(LABELS_PATH) as f:
    CLASS_NAMES = [line.strip() for line in f if line.strip()]
print(f"Classes ({len(CLASS_NAMES)}): {CLASS_NAMES}")

MATERIAL_DB = {}
ALL_MATERIALS = []
with open(MATERIAL_DB_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        material_key = row["Material"].strip().lower()
        MATERIAL_DB[material_key] = row
        ALL_MATERIALS.append({
            "material": row["Material"].strip(),
            "fibre_type": row["Fibre Type"].strip(),
            "sustainability_category": row["Sustainability Category"].strip(),
            "reason": row["Reason/Criteria"].strip()
        })
print(f"Loaded {len(MATERIAL_DB)} materials from material_database.csv")


def preprocess_image(file_bytes):
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    img = img.resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32)
    arr = np.expand_dims(arr, axis=0)
    return arr


@app.route("/health", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "Fabric AI Python Inference Engine",
        "model": "MobileNetV2 Transfer Learning",
        "classes": CLASS_NAMES,
        "database_count": len(MATERIAL_DB)
    })


@app.route("/api/materials", methods=["GET"])
def materials():
    return jsonify({
        "status": "ok",
        "materials": ALL_MATERIALS
    })


@app.route("/predict", methods=["POST"])
@app.route("/api/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No 'image' file in request"}), 400

    file = request.files["image"]
    if not file.filename:
        return jsonify({"error": "Empty file uploaded"}), 400

    try:
        arr = preprocess_image(file.read())
    except Exception as e:
        return jsonify({"error": f"Could not read image: {e}"}), 400

    predictions = model.predict(arr)[0]  # shape: (num_classes,)
    top_idx = int(np.argmax(predictions))
    top_label = CLASS_NAMES[top_idx]
    top_confidence = float(predictions[top_idx])

    # Capitalize for display consistency while keeping lookup lowercased
    display_label = top_label.capitalize()

    # Full ranked breakdown
    ranked = sorted(
        [
            {
                "fabric": CLASS_NAMES[i].capitalize(),
                "confidence": float(predictions[i])
            }
            for i in range(len(CLASS_NAMES))
        ],
        key=lambda x: x["confidence"],
        reverse=True,
    )

    material_info = MATERIAL_DB.get(top_label.lower())
    if material_info:
        sustainability = {
            "fibre_type": material_info["Fibre Type"],
            "category": material_info["Sustainability Category"],
            "reason": material_info["Reason/Criteria"],
        }
    else:
        sustainability = {
            "fibre_type": "Natural" if top_label.lower() in ["cotton", "linen", "silk", "wool"] else "Synthetic",
            "category": "Eco-Friendly" if top_label.lower() in ["cotton", "linen", "silk", "wool"] else "Non-Eco-Friendly",
            "reason": f"Standard profile for {display_label} material.",
        }

    return jsonify({
        "fabric_type": display_label,
        "confidence": top_confidence,
        "ranked_predictions": ranked,
        "sustainability": sustainability,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Fabric AI Python backend on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
