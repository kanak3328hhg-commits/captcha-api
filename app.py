import os
import requests
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

app = Flask(__name__)
CORS(app)

def get_session():
    session = requests.Session()
    # DNS এবং নেটওয়ার্ক সমস্যা এড়াতে শক্তিশালী ৫ বার রিট্রাই লজিক
    retry = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    return session

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        img_b64 = data.get('full_grid')
        target = data.get('target', 'object') # ব্রাউজার থেকে পাঠানো ডাইনামিক নাম
        
        API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2-VL-7B-Instruct"
        headers = {"Authorization": f"Bearer {os.environ.get('HF_API_TOKEN')}"}
        
        payload = {
            "inputs": {
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                        {"type": "text", "text": f"This is a 3x3 grid indexed 0 to 8. Find all indexes containing '{target}'. Return ONLY the matching numbers separated by commas, for example: 1,3,5. If none match, return empty."}
                    ]
                }]
            }
        }
        
        response = get_session().post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            ai_response = str(response.json())
            # এআই এর উত্তর থেকে শুধু সংখ্যাগুলো (0-8) ছেঁকে নেওয়া
            found_indexes = [int(x) for x in re.findall(r'[0-8]', ai_response)]
            return jsonify({"click_indexes": list(set(found_indexes))})
        else:
            return jsonify({"error": f"HuggingFace error: {response.text}", "click_indexes": []}), 500
            
    except Exception as e:
        return jsonify({"error": str(e), "click_indexes": []}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
