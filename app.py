from flask import Flask, request, jsonify
import requests
import os
from flask_cors import CORS  # Para evitar errores CORS

app = Flask(__name__)
CORS(app)  # Permite solicitudes desde cualquier origen

API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": user_message}]
    }
    response = requests.post(API_URL, headers=headers, json=data)
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)