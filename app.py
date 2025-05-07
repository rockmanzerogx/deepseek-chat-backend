from flask import Flask, request, jsonify
import requests
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources=
     {r"/chat": {
         "origins": ["https://rockmanzerogx.github.io","http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:3000"]
                                
        }})

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
    ai_response = response.json()["choices"][0]["message"]["content"]
    return jsonify({"response": ai_response})  # Estructura clave

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)