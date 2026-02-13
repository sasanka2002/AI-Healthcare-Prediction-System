from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
import sqlite3
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import LogisticRegression
from textblob import TextBlob

# =========================
# Flask Setup
# =========================
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'healthcare-secret-key'
jwt = JWTManager(app)

# =========================
# Database Setup
# =========================
def get_db():
    return sqlite3.connect("users.db")

with get_db() as db:
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

# =========================
# AI / ML MODELS
# =========================

# Content-based (Disease)
health_data = {
    "disease": ["Diabetes", "Hypertension", "Heart Disease", "Flu"],
    "symptoms": [
        "high sugar fatigue urination",
        "high blood pressure headache",
        "chest pain breathlessness fatigue",
        "fever cough cold headache"
    ]
}
df = pd.DataFrame(health_data)
vectorizer = TfidfVectorizer()
vectors = vectorizer.fit_transform(df["symptoms"])

def recommend_disease(symptoms):
    vec = vectorizer.transform([symptoms])
    sim = cosine_similarity(vec, vectors)
    return df.iloc[sim.argmax()]["disease"]

# Disease prediction (ML)
X = np.array([
    [45, 140, 180, 85],
    [50, 150, 200, 90],
    [30, 120, 90, 70],
    [25, 110, 85, 68]
])
y = [1, 1, 0, 0]
model = LogisticRegression()
model.fit(X, y)

# =========================
# AUTH ROUTES
# =========================
@app.route("/home")
def home_page():
    return render_template("home.html")


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form
        try:
            with get_db() as db:
                db.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (data["username"], data["password"])
                )
            return redirect("/login")
        except:
            return "User already exists"
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        with get_db() as db:
            user = db.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (data["username"], data["password"])
            ).fetchone()

        if user:
            token = create_access_token(identity=data["username"])
            return redirect(url_for("dashboard", token=token))
        return "Invalid credentials"
    return render_template("login.html")

# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/recommend", methods=["POST"])
@jwt_required()
def recommend():
    data = request.json
    disease = recommend_disease(data["symptoms"])
    prediction = model.predict([[48, 145, 190, 88]])[0]
    sentiment = TextBlob(data["review"]).sentiment.polarity

    return jsonify({
        "disease": disease,
        "prediction": int(prediction),
        "sentiment": "Positive" if sentiment > 0 else "Negative"
    })

# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)
