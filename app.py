from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import requests
import os

app = Flask(__name__)
CORS(app)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    img_b64 = data.get('full_grid')
    target = data.get('target')

    # হাগিং ফেস রিকোয়েস্ট
    API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2-VL-7B-Instruct"
    headers = {"Authorization": f"Bearer {os.environ.get('HF_API_TOKEN')}"}
    
    payload = {
        "inputs": {
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                    {"type": "text", "text": f"Find '{target}' in this 3x3 grid. Return indexes 0-8 separated by comma."}
                ]
            }]
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    # এখানে রেসপন্স প্রসেস করে ইনডেক্স রিটার্ন করুন
    return jsonify({"click_indexes": [0, 1, 2]}) # উদাহরণ
