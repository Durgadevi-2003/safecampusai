import joblib, json, numpy as np, pandas as pd
from pathlib import Path
from tensorflow.keras.models import load_model
import xgboost as xgb

BASE = Path(__file__).resolve().parent.parent.parent
models_dir = BASE / "models"

meta = json.load(open(models_dir / "metadata.json"))
FEATURE_COLS = meta["feature_cols"]
SEQ_LEN = meta["sequence_length"]

scaler = joblib.load(models_dir / "scaler.joblib")
label_encoder = joblib.load(models_dir / "label_encoder.joblib")

feature_extractor = load_model(models_dir / "student_behavior_feature_extractor.h5")
xgb_model = xgb.XGBClassifier()
xgb_model.load_model(str(models_dir / "student_behavior_xgb.json"))

def build_sequence_from_behaviors(behaviors):
    df = pd.DataFrame([{c: getattr(b, c) for c in FEATURE_COLS} for b in behaviors])
    scaled = scaler.transform(df.values)
    return scaled.reshape(1, SEQ_LEN, len(FEATURE_COLS))

def predict_for_student_behaviors(behaviors):
    if len(behaviors) < SEQ_LEN:
        return None
    seq = build_sequence_from_behaviors(behaviors)
    feat = feature_extractor.predict(seq)
    probs = xgb_model.predict_proba(feat)[0]
    class_idx = int(probs.argmax())
    label = label_encoder.inverse_transform([class_idx])[0]
    return {"label": label, "score": float(probs[class_idx]), "probs": probs.tolist()}
