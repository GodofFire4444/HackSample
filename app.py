import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template # Import render_template
from dotenv import load_dotenv

# --- INITIALIZATION ---
load_dotenv()
app = Flask(__name__, template_folder='templates') # Tell Flask where to find templates

# --- GEMINI AI CONFIGURATION ---
try:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    print(f"--- FATAL ERROR: Failed to configure Gemini AI. ---")
    print(f"Error details: {e}")
    model = None

# --- PROMPT ENGINEERING ---
PROMPT_TEMPLATES = {
    "summary": """
        You are an expert analyst. Your primary task is to generate a concise and accurate summary...
    """,
    "quick-quiz": """
        You are a helpful quiz generator...
    """,
    "flash-card": """
        You are a flashcard creator...
    """,
    "translate": """
        You are a language translator...
    """
} # (Prompts are truncated for brevity, use your full prompts)


# --- NEW ROUTE TO SERVE THE FRONTEND ---
@app.route("/")
def index():
    """Serves the main index.html file."""
    return render_template('index.html')


# --- API ENDPOINT ---
@app.route("/api/agent", methods=["POST"])
def handle_agent_request():
    if not model:
        return jsonify({"reply": "Error: The AI model is not configured on the server."}), 500

    task = request.form.get("task")
    message = request.form.get("message")
    language = request.form.get("language")
    files = request.files.getlist("files[]")

    if not task:
        return jsonify({"reply": "Error: 'task' is a required field."}), 400
    if task not in PROMPT_TEMPLATES:
        return jsonify({"reply": f"Error: Task '{task}' is not a valid task."}), 400

    prompt_template = PROMPT_TEMPLATES[task]
    formatted_prompt = prompt_template.format(message=message, language=language)
    
    api_parts = [formatted_prompt]
    for file in files:
        api_parts.append({
            "mime_type": file.mimetype,
            "data": file.read()
        })
        
    try:
        response = model.generate_content(api_parts)
        return jsonify({"reply": response.text})
    except Exception as e:
        print(f"An error occurred during Gemini API call: {e}")
        return jsonify({"reply": f"An error occurred while contacting the AI: {e}"}), 500

# Note: We remove the app.run() block for production.
# The Gunicorn server will run the app.