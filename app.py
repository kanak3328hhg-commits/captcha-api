# ========================================================
# পাইথন ব্যাকএন্ড: app.py (সম্পূর্ণ এবং সংশোধিত কোড)
# ========================================================

import os
import requests
import re
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

def create_robust_session():
    session = requests.Session()
    retries = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

http_session = create_robust_session()

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON payload", "click_indexes": []}), 400
            
        img_b64 = data.get('full_grid')
        target = data.get('target', 'object')
        
        if isinstance(target, str):
            target = target.strip()
        
        if not img_b64:
            return jsonify({"error": "Missing full_grid image data", "click_indexes": []}), 400

        API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2-VL-7B-Instruct"
        
        token = os.environ.get('HF_API_TOKEN')
        if not token:
            logger.error("HF_API_TOKEN missing!")
            return jsonify({"error": "Missing API Token", "click_indexes": []}), 500
            
        headers = {"Authorization": f"Bearer {token}"}
        
        # 🎯 প্রম্পট পরিবর্তন: এআই-কে শুধু ব্র্যাকেটের ভেতর উত্তর দিতে বাধ্য করা হয়েছে
        payload = {
            "inputs": {
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                        {"type": "text", "text": f"This is a 3x3 image grid indexed from 0 to 8. Identify all individual tile indexes that contain '{target}'. Your response must ONLY contain the index numbers inside square brackets, for example: [1, 4, 7]. If no tiles match, return []. Do not write any other explanation or list numbering."}
                    ]
                }]
            },
            "options": {"wait_for_model": True}
        }
        
        logger.info(f"Sending request to HuggingFace. Target: {target}")
        response = http_session.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            ai_response = str(response.json())
            logger.info(f"AI Raw Response: {ai_response}")
            
            # 🎯 রেগুলার এক্সপ্রেশন ফিক্স: প্রথমে স্কয়ার ব্র্যাকেট [...] খুঁজে তার ভেতরের সংখ্যা বের করা
            bracket_match = re.search(r'\[(.*?)\]', ai_response)
            if bracket_match:
                inside_content = bracket_match.group(1)
                found_indexes = [int(x) for x in re.findall(r'[0-8]', inside_content)]
                click_indexes = sorted(list(set(found_indexes)))
            else:
                click_indexes = []
                
            logger.info(f"Filtered Click Indexes: {click_indexes}")
            return jsonify({"click_indexes": click_indexes})
        else:
            logger.error(f"HuggingFace API Error {response.status_code}: {response.text}")
            return jsonify({"error": f"HuggingFace Error {response.status_code}", "click_indexes": []}), 502
            
    except Exception as e:
        logger.error(f"Internal error: {str(e)}")
        return jsonify({"error": str(e), "click_indexes": []}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
