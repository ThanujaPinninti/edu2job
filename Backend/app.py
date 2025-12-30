# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from config import SECRET_KEY
from auth import auth_blueprint
from profile import profile_blueprint
import joblib
import numpy as np
import os
import datetime


app = Flask(__name__, static_folder="frontend", template_folder="frontend")
CORS(app)

app.secret_key = SECRET_KEY

model = joblib.load("job_model.pkl")
le_degree = joblib.load("le_degree.pkl")
le_spec = joblib.load("le_spec.pkl")
le_job = joblib.load("le_job.pkl")
mlb_skills = joblib.load("mlb_skills.pkl")
mlb_certs = joblib.load("mlb_certs.pkl")
model_accuracy = joblib.load("model_accuracy.pkl")

app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(profile_blueprint, url_prefix="/profile")

@app.route("/", methods=["GET"])
def home():
    return {"message": "EDU2JOB Backend Running!!!!......."}

@app.route("/job/predict", methods=["POST"])
def predict_job():
    data = request.json
    def safe_encode(encoder, value):
        if value in encoder.classes_:
            return encoder.transform([value])[0]
        return -1
    degree = safe_encode(le_degree, data["degree"])
    specialization = safe_encode(le_spec, data["specialization"])
    cgpa = float(data["cgpa"])
    skills = data.get("skills", [])
    certs = data.get("certifications", [])
    skills = [s.strip() for s in skills if s.strip()]
    certs = [c.strip() for c in certs if c.strip()]
    if not skills:
        skills = ["None"]
    if not certs:
        certs = ["None"]
    skills_encoded = mlb_skills.transform([skills])
    certs_encoded = mlb_certs.transform([certs])
    X = np.concatenate(
        [
            np.array([[degree, specialization, cgpa]]),
            skills_encoded,
            certs_encoded
        ],
        axis=1
    )
    probs = model.predict_proba(X)[0]
    top_idx = probs.argsort()[-4:][::-1]
    top_probs = probs[top_idx]
    total = top_probs.sum()
    predictions = []
    for idx, p in zip(top_idx, top_probs):
        predictions.append({
            "role": le_job.inverse_transform([idx])[0],
            "confidence": round((p / total) * 100)
        })
    return jsonify({"predictions": predictions})

@app.route("/job/accuracy", methods=["GET"])
def get_accuracy():
    return {"accuracy": round(model_accuracy * 100, 2)}

@app.route('/feedback', methods=['POST'])
def save_feedback():
    data = request.get_json()
    rating = data.get('rating')
    feedback = data.get('feedback')
    if rating and feedback:
        with open("feedbacks.txt", "a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} | Rating: {rating} | Feedback: {feedback}\n")
        return jsonify({"message": "Feedback saved!"}), 200
    return jsonify({"message": "Invalid input."}), 400

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
