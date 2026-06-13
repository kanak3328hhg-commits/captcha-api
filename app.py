import os
import requests
import numpy as np
import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# এক্সটেনশনের সিকিউরিটি ও CSP দেয়াল ভাঙার জন্য CORS পুরোপুরি ওপেন করা হলো
CORS(app, resources={r"/*": {"origins": "*"}}) 

def process_captcha(image_url, target_text):
    try:
        response = requests.get(image_url, timeout=10)
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            return []

        h, w, _ = img.shape
        rows, cols = 3, 3
        
        click_indexes = []
        index = 0
        
        # 🌟 টেস্ট করার জন্য ২/৩টি বক্সে ডেমো ক্লিক জেনারেট করা হচ্ছে
        for r in range(rows):
            for c in range(cols):
                if (r + c) % 2 == 0: 
                    click_indexes.append(index)
                index += 1
                
        return click_indexes
    except Exception as e:
        print("Error during processing:", e)
        return []

@app.route('/')
def home():
    return "AI Captcha Backend is Running Successfully!"

# পোস্ট মেথড রাউট
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data or 'image_url' not in data:
        return jsonify({"error": "Missing image_url"}), 400
    
    image_url = data['image_url']
    target = data.get('target', '').lower()
    
    tiles_to_click = process_captcha(image_url, target)
    
    # রেসপন্স হেডারে এক্সপ্রেশন ক্লিয়ার রাখা
    return jsonify({"click_indexes": tiles_to_click})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
