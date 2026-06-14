import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

app = Flask(__name__)
CORS(app)

# রিট্রাই লজিক যোগ করা হয়েছে
def get_huggingface_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        img_b64 = data.get('full_grid')
        target = data.get('target', 'object')
        
        API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2-VL-7B-Instruct"
        headers = {"Authorization": f"Bearer {os.environ.get('HF_API_TOKEN')}"}
        
        # সেশন ব্যবহার করে রিকোয়েস্ট পাঠানো
        response = get_huggingface_session().post(API_URL, headers=headers, json={
            "inputs": {"messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                {"type": "text", "text": f"Find '{target}' (0-8). Return ONLY comma-separated numbers."}
            ]}]}
        }, timeout=60)
        
        return jsonify({"click_indexes": [0, 4]}) # এখানে এআই রেসপন্স প্রসেসিং লজিক বসান
    except Exception as e:
        return jsonify({"error": str(e)}), 500
