import os
import requests
import numpy as np
import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # এক্সটেনশন থেকে রিকোয়েস্ট আসার অনুমতি দেওয়ার জন্য

# ইমেজ প্রসেসিং এবং ডেমো অবজেক্ট ডিটেকশন ফাংশন
def process_captcha(image_url, target_text):
    try:
        # ১. ইমেজ ডাউনলোড করা
        response = requests.get(image_url, timeout=10)
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            return []

        # এখানে একটি বেসিক গ্রিড এনালাইসিস সিমুলেশন করা হচ্ছে
        # যেহেতু এটি ফ্রি এবং লাইটওয়েট, আমরা ইমেজ সাইজ অনুযায়ী ৩x৩ গ্রিডে ভাগ করছি
        h, w, _ = img.shape
        rows, cols = 3, 3
        tile_h, tile_w = h // rows, w // cols
        
        click_indexes = []
        index = 0
        
        # প্রতিটি ঘরের ছবি এনালাইসিস (এখানে ডেমো হিসেবে র্যান্ডমলি কিছু বক্স সিলেক্ট হবে)
        # আপনি যখন টেস্ট করবেন, এটি কাজ করছে কিনা তা নিশ্চিত করার জন্য ২/৩টি বক্সে ক্লিক পাঠাবে
        for r in range(rows):
            for c in range(cols):
                # বাস্তব এআই এখানে অবজেক্ট খুঁজতো, আমরা আপাতত টেস্ট করার জন্য লজিক রাখছি
                if (r + c) % 2 == 0: 
                    click_indexes.append(index)
                index += 1
                
        return click_indexes
    except Exception as e:
        print("Error:", e)
        return []

@app.route('/')
def home():
    return "AI Captcha Backend is Running Successfully!"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data or 'image_url' not in data:
        return jsonify({"error": "Missing image_url"}), 400
    
    image_url = data['image_url']
    target = data.get('target', '').lower()
    
    # ক্যাপচা সলভ করা
    tiles_to_click = process_captcha(image_url, target)
    
    return jsonify({"click_indexes": tiles_to_click})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)