import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

app = Flask(__name__)
CORS(app)

# নেটওয়ার্ক কানেকশন ঠিক রাখার জন্য সেশন তৈরি
def get_session():
    session = requests.Session()
    retry = Retry(connect=5, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    return session

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        img_b64 = data.get('full_grid')
        target = data.get('target', 'object')
        
        API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2-VL-7B-Instruct"
        headers = {"Authorization": f"Bearer {os.environ.get('HF_API_TOKEN')}"}
        
        payload = {
            "inputs": {
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                        {"type": "text", "text": f"Find index 0-8 containing '{target}'. Return comma-separated numbers."}
                    ]
                }]
            }
        }
        
        response = get_session().post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        # এখান থেকে এআই-এর রেসপন্স প্রসেস করুন
        return jsonify({"click_indexes": [0, 4]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
