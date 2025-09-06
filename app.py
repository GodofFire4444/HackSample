from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
import google.generativeai as genai
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
CORS(app)

# Set your Gemini API key here
GENAI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

def get_history():
    if "history" not in session:
        session["history"] = []
    return session["history"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_text = data.get("text", "").strip()
    task = data.get("task")
    lang = data.get("lang")

    if not task or not lang or not user_text:
        return jsonify({"error": "Missing required fields."}), 400

    # Save user message
    history = get_history()
    history.append({"role": "user", "text": user_text, "task": task, "lang": lang})

    # Compose prompt for Gemini
    prompt = f"Task: {task}\nLanguage: {lang}\nUser: {user_text}\n"
    try:
        response = model.generate_content(prompt)
        ai_reply = response.text
    except Exception as e:
        ai_reply = "Sorry, I couldn't get an answer from Gemini AI."

    history.append({"role": "ai", "text": ai_reply})
    session["history"] = history[-20:]

    return jsonify({"reply": ai_reply, "history": session["history"]})

if __name__ == "__main__":
    app.run(debug=True)
