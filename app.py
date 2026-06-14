import os
import requests
import re
import socket
from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

app = Flask(__name__)
CORS(app)

def get_session():
    session = requests.Session()
    # ৫ বার পর্যন্ত কানেকশন রিট্রাই করবে যদি নেটওয়ার্ক ড্রপ করে
    retry = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
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
                        {"type": "text", "text": f"This is a 3x3 image grid indexed from 0 to 8. Find all individual tile indexes that contain '{target}'. Return ONLY the numbers separated by commas (e.g., 1,4,7). If nothing matches, return empty."}
                    ]
                }]
            }
        }
        
        response = get_session().post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            ai_response = str(response.json())
            # রেজেক্স দিয়ে শুধুমাত্র ০ থেকে ৮ এর ভেতরের সংখ্যাগুলো বের করা হচ্ছে
            found_indexes = [int(x) for x in re.findall(r'[0-8]', ai_response)]
            return jsonify({"click_indexes": list(set(found_indexes))})
        else:
            return jsonify({"error": f"HuggingFace API Node Error: {response.text}", "click_indexes": []}), 500
            
    except Exception as e:
        return jsonify({"error": str(e), "click_indexes": []}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
