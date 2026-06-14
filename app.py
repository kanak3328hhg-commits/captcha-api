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

# লগিং কনফিগারেশন
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# নেটওয়ার্ক ফেইলুর হ্যান্ডেল করার জন্য রোবাস্ট সেশন মেকানিজম
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

        # 🎯 পরিবর্তন ১: Hugging Face-এর সঠিক OpenAI-compatible চ্যাট এন্ডপয়েন্ট ইউআরএল
        API_URL = "https://api-inference.huggingface.co/v1/chat/completions"
        
        token = os.environ.get('HF_API_TOKEN')
        if not token:
            logger.error("HF_API_TOKEN Environment Variable missing!")
            return jsonify({"error": "Missing API Token Configuration", "click_indexes": []}), 500
            
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 🎯 পরিবর্তন ২: সঠিক পে-লোড ফরম্যাট (মডেল নেম এবং ম্যাক্স টোকেনসহ)
        payload = {
            "model": "Qwen/Qwen2-VL-7B-Instruct",
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": f"This is a 3x3 image grid indexed from 0 to 8. Identify all individual tile indexes that contain '{target}'. Your response must ONLY contain the index numbers inside square brackets, for example: [1, 4, 7]. If no tiles match, return []. Do not write any other explanation."
                    },
                    {
                        "type": "image_url", 
                        "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                    }
                ]
            }],
            "max_tokens": 40,
            "options": {"wait_for_model": True}
        }
        
        logger.info(f"Sending request to HuggingFace Chat Endpoint. Target: {target}")
        response = http_session.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            res_json = response.json()
            
            # 🎯 পরিবর্তন ৩: সঠিক চ্যাট ফরম্যাট থেকে টেক্সট রেসপন্স এক্সট্র্যাক্ট করা
            if "choices" in res_json and len(res_json["choices"]) > 0:
                ai_response = res_json["choices"][0]["message"]["content"]
                logger.info(f"AI Content Response: {ai_response}")
                
                # স্কয়ার ব্র্যাকেটের ভেতরের অংশ পার্স করা
                bracket_match = re.search(r'\[(.*?)\]', ai_response)
                if bracket_match:
                    inside_content = bracket_match.group(1)
                    found_indexes = [int(x) for x in re.findall(r'[0-8]', inside_content)]
                else:
                    # যদি মডেল কোনো কারণে ব্র্যাকেট না দেয়, তবে ব্যাকআপ হিসেবে পুরো টেক্সট থেকে নম্বর নেবে
                    found_indexes = [int(x) for x in re.findall(r'[0-8]', ai_response)]
                    
                click_indexes = sorted(list(set(found_indexes)))
                logger.info(f"Final Filtered Click Indexes: {click_indexes}")
                return jsonify({"click_indexes": click_indexes})
            else:
                logger.error(f"Unexpected JSON structure from HuggingFace: {res_json}")
                return jsonify({"error": "Unexpected AI response format", "click_indexes": []}), 502
                
        else:
            logger.error(f"HuggingFace API Error {response.status_code}: {response.text}")
            return jsonify({
                "error": f"HuggingFace API Code {response.status_code}",
                "details": response.text,
                "click_indexes": []
            }), 502
            
    except Exception as e:
        logger.error(f"Unexpected internal server error: {str(e)}")
        return jsonify({"error": str(e), "click_indexes": []}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
