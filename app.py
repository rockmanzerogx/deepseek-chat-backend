from flask import Flask, request, jsonify, make_response
import requests
import os
from PyPDF2 import PdfReader
from flask_cors import CORS

app = Flask(__name__)

# Configuración CORS mejorada
cors = CORS(app, resources={
    r"/chat": {
        "origins": [
            "https://rockmanzerogx.github.io",
            "http://localhost:*",
            "http://127.0.0.1:*"
        ],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

chat_history = {}

def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return ""

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "https://rockmanzerogx.github.io")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response

    try:
        # Manejar datos JSON o FormData
        if request.content_type == "application/json":
            data = request.get_json()
            user_message = data.get("message")
            uploaded_file = None
        else:
            user_message = request.form.get("message")
            uploaded_file = request.files.get("document")

        # Procesar archivo
        document_text = ""
        if uploaded_file and uploaded_file.filename:
            if uploaded_file.filename.lower().endswith(".pdf"):
                document_text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.filename.lower().endswith(".txt"):
                document_text = uploaded_file.read().decode("utf-8")

        # Construir prompt
        full_prompt = f"Documento:\n{document_text}\n\nPregunta: {user_message}" if document_text else user_message

        # Llamar a API DeepSeek
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": full_prompt}],
            "max_tokens": 1000
        }

        api_response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        api_response.raise_for_status()
        
        ai_response = api_response.json()["choices"][0]["message"]["content"]
        
        return jsonify({
            "response": ai_response,
            "status": "success"
        })

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)