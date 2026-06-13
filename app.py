import os
import base64
import numpy as np
import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def process_captcha_base64(base64_string, target_text):
    try:
        # base64 ডাটা থেকে সরাসরি ইমেজ ডিকোড করা (ডাউনলোড করার কোনো ঝামেলা নেই)
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
            
        img_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return []

        h, w, _ = img.shape
        rows, cols = 3, 3
        
        click_indexes = []
        index = 0
        
        # ডেমো ক্লিক জেনারেটর (টেস্টিং লজিক)
        for r in range(rows):
            for c in range(cols):
                if (r + c) % 2 == 0: 
                    click_indexes.append(index)
                index += 1
                
        return click_indexes
    except Exception as e:
        print("Error during image processing:", e)
        return []

@app.route('/')
def home():
    return "New Screen-Capture AI Backend is Running Successfully!"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data or 'image_data' not in data:
        return jsonify({"error": "Missing image_data"}), 400
    
    # নতুন সিস্টেম: লিংকের বদলে বেস৬৪ ইমেজ ডাটা গ্রহণ
    base64_image = data['image_data']
    target = data.get('target', '').lower()
    
    tiles_to_click = process_captcha_base64(base64_image, target)
    return jsonify({"click_indexes": tiles_to_click})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
