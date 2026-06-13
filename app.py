import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2-VL-7B-Instruct"
HF_API_TOKEN = os.environ.get("HF_API_TOKEN") or "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"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

@app.route('/')
def home():
    return "Hugging Face Captcha Solver Matrix is Active!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"click_indexes": []})
        
        target_text = data.get('target', '').lower().strip()
        # এখানে আমরা প্রতিটি আলাদা টাইলের বদলে পুরো গ্রিডের ১টি কম্বাইন্ড বেস৬৪ ইমেজ রিসিভ করব
        full_grid_b64 = data.get('full_grid', '') 
        
        if not full_grid_b64:
            print("⚠️ No snapshot image received.")
            return jsonify({"click_indexes": []})

        print(f"🤖 Target Object to Find: '{target_text}'")

        # Hugging Face-এর সঠিক ভিশন ডাটা স্ট্রাকচার প্যালোডের ফরম্যাট
        payload = {
            "inputs": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "image": full_grid_b64 # বেস৬৪ ডাটা স্ট্রিং সরাসরি ইনপুট
                            },
                            {
                                "type": "text",
                                "text": f"This image is a 3x3 grid layout containing 9 small pictures. The slots are indexed from 0 to 8 (Row 1: 0,1,2; Row 2: 3,4,5; Row 3: 6,7,8). Identify which slot indexes contain a '{target_text}'. Return ONLY the numbers separated by commas (e.g. 0, 4, 5). If no matching item found, reply 'None'."
                            }
                        ]
                    }
                ]
            }
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        click_indexes = []

        if response.status_code == 200:
            res_json = response.json()
            ai_response = ""
            if isinstance(res_json, list) and len(res_json) > 0:
                ai_response = res_json[0].get('generated_text', '')
            elif isinstance(res_json, dict):
                ai_response = res_json.get('generated_text', '')

            print(f"🧠 Raw AI Decision: {ai_response}")
            
            # রেসপন্স থেকে সংখ্যাগুলো ফিল্টার করে নেওয়া
            for word in ai_response.replace(",", " ").replace("[", "").replace("]", "").split():
                if word.isdigit():
                    num = int(word)
                    if 0 <= num <= 8:
                        click_indexes.append(num)
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")

        print(f"🎯 Final Dispatched Clicks: {click_indexes}")
        return jsonify({"click_indexes": click_indexes})

    except Exception as e:
        print(f"🚨 Python Crash Log: {str(e)}")
        return jsonify({"click_indexes": []})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
