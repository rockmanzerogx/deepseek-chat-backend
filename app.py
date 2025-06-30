from flask import Flask, request, jsonify
import requests
import os
from PyPDF2 import PdfReader
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={
    r"/chat": {
        "origins": ["https://rockmanzerogx.github.io"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

API_KEY = os.getenv("DEEPSEEK_API_KEY")  # Usa variables de entorno
API_URL = "https://api.deepseek.com/v1/chat/completions"

# Cache de conversación (puedes usar una DB en producción)
chat_history = {}

def extract_text_from_pdf(pdf_file):
    """Extrae texto de un archivo PDF."""
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")
    session_id = data.get("session_id", "default")  # ID para mantener contexto
    uploaded_file = request.files.get("document")  # Archivo subido (PDF/TXT)

    # 1. Procesar documento si se subió
    document_text = ""
    if uploaded_file:
        if uploaded_file.filename.endswith(".pdf"):
            document_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.filename.endswith(".txt"):
            document_text = uploaded_file.read().decode("utf-8")

    # 2. Combinar documento + pregunta (si existe)
    full_prompt = (
        f"Contexto del documento:\n{document_text}\n\n"
        f"Pregunta: {user_message}"
        if document_text else user_message
    )

    # 3. Mantener historial de conversación
    if session_id not in chat_history:
        chat_history[session_id] = []
    
    chat_history[session_id].append({"role": "user", "content": full_prompt})

    # 4. Llamar a la API de DeepSeek
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat",
        "messages": chat_history[session_id],
        "max_tokens": 1000,
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Lanza error si HTTP != 200
        ai_response = response.json()["choices"][0]["message"]["content"]
        
        # Guardar respuesta en el historial
        chat_history[session_id].append({"role": "assistant", "content": ai_response})
        
        return jsonify({"response": ai_response, "session_id": session_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)