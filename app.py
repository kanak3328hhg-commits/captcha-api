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
        target = data.get('target', 'object').refresh()
        
        if not img_b64:
            return jsonify({"error": "Missing full_grid image data", "click_indexes": []}), 400

        API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2-VL-7B-Instruct"
        
        token = os.environ.get('HF_API_TOKEN')
        if not token:
            logger.error("HF_API_TOKEN পাওয়া যায়নি!")
            return jsonify({"error": "Missing API Token Configuration", "click_indexes": []}), 500
            
        headers = {"Authorization": f"Bearer {token}"}
        
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
        
        logger.info(f"HuggingFace Request Sent. Target Object: {target}")
        
        response = http_session.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            ai_response = str(response.json())
            logger.info(f"AI Raw Response: {ai_response}")
            
            found_indexes = [int(x) for x in re.findall(r'[0-8]', ai_response)]
            click_indexes = sorted(list(set(found_indexes))) 
            
            return jsonify({"click_indexes": click_indexes})
        else:
            logger.error(f"HuggingFace API Node Error {response.status_code}: {response.text}")
            return jsonify({"error": f"HuggingFace Error {response.status_code}", "click_indexes": []}), 502
            
    except Exception as e:
        logger.error(f"Unexpected internal server error: {str(e)}")
        return jsonify({"error": str(e), "click_indexes": []}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
