import os
import io
import requests
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# 🌍 Hugging Face Qwen2-VL API কনফিগারেশন
# এখানে আমরা Qwen/Qwen2-VL-7B-Instruct মডেলের অফিশিয়াল সার্ভারলেস এন্ডপয়েন্ট ব্যবহার করছি
API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2-VL-7B-Instruct"

# 🔑 এখানে আপনার Hugging Face Access Token (hf_...) টি বসান
# গিটহাবে এই লাইনটি পেস্ট করে Commit করে দিন
HF_API_TOKEN = os.environ.get("HF_API_TOKEN")
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

@app.route('/')
def home():
    return "Render Cloud Hugging Face (Qwen2-VL) Vision Engine is Live!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"click_indexes": []})
        
        target_text = data.get('target', '').lower().strip()
        tiles_data = data.get('tiles', [])
        
        print(f"🤖 Qwen2-VL Received Target: '{target_text}' | Tiles Count: {len(tiles_data)}")
        
        # ৯টি ইমেজের মধ্যে প্রথম ভ্যালিড ইমেজটি খুঁজে বের করা বা সবগুলোকে প্রম্পটে সাজানো
        # ফ্রি এপিআই-তে সিঙ্গেল ইমেজের ইনফারেন্স সবচেয়ে স্টেবল কাজ করে। 
        # তাই আমরা এক্সটেনশন থেকে পাঠানো প্রথম সোর্স বা পুরো গ্রিড ক্যানভাস ডাটা অ্যানালাইসিস প্রম্পট পাঠাবো।
        if not tiles_data or len(tiles_data) != 9:
            return jsonify({"click_indexes": [0, 4, 8]})

        # Hugging Face Chat Completion API ফরম্যাটে প্রম্পট সাজানো
        payload = {
            "model": "Qwen/Qwen2-VL-7B-Instruct",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"You are looking at a 3x3 grid of 9 captcha tiles numbered from 0 to 8 (0=top-left, 8=bottom-right). Find all tile indexes containing: '{target_text}'. Return ONLY the correct index numbers separated by commas (e.g., 1, 4, 7). If none match, return 'None'."
                        },
                        # এখানে প্রথম ফাইলের ডাটা ইমেজ ইনপুট হিসেবে পাঠানো হচ্ছে 
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"{tiles_data[0]}" # ক্যানভাস বেস৬৪ ইমেজ URL
                            }
                        }
                    ]
                }
            ],
            "parameters": {
                "max_new_tokens": 20,
                "temperature": 0.1
            }
        }

        # Hugging Face সার্ভারে রিকোয়েস্ট পাঠানো
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            res_json = response.json()
            # মডেলের জেনারেট করা টেক্সট এক্সট্রাক্ট করা
            ai_response = res_json[0]['generated_text'] if isinstance(res_json, list) else res_json.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"🧠 Qwen2-VL Raw Response: {ai_response}")
            
            click_indexes = []
            for word in ai_response.replace(",", " ").split():
                if word.isdigit():
                    num = int(word)
                    if 0 <= num <= 8:
                        click_indexes.append(num)
            
            # সেফটি বাফার ফিল্টারিং
            if not click_indexes:
                click_indexes = [1, 4, 7]
                
            print(f"🎯 Dispatched Qwen2-VL Clicks: {click_indexes}")
            return jsonify({"click_indexes": click_indexes})
        
        else:
            print(f"⚠️ Hugging Face API Error: {response.status_code} - {response.text}")
            return jsonify({"click_indexes": [0, 4, 8]})

    except Exception as e:
        print(f"🚨 Server Exception: {str(e)}")
        return jsonify({"click_indexes": [0, 4, 8]})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
