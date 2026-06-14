import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

app = Flask(__name__)
CORS(app)

def get_session():
    session = requests.Session()
    # কানেকশন ব্যর্থ হলে পুনরায় চেষ্টা করার লজিক
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    return session

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    img_b64 = data.get('full_grid')
    target = data.get('target', 'object')
    
    API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2-VL-7B-Instruct"
    headers = {"Authorization": f"Bearer {os.environ.get('HF_API_TOKEN')}"}
    
    payload = {
        "inputs": {"messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
            {"type": "text", "text": f"Find index 0-8 for '{target}'"}
        ]}]}
    }
    
    try:
        # রিট্রাই সেশন ব্যবহার করে পোস্ট রিকোয়েস্ট
        response = get_session().post(API_URL, headers=headers, json=payload, timeout=45)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
