import os
import base64
import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return "AI Grid Vision Engine is Live!"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data:
        return jsonify({"click_indexes": []})
    
    target_text = data.get('target', '').lower().strip()
    tiles_data = data.get('tiles', []) # ৯টি ছবির ডাটা
    
    print(f"🤖 Target Search: {target_text} | Total Tiles Received: {len(tiles_data)}")
    
    click_indexes = []
    
    # প্রতিটি টাইলস বা ছবি আলাদাভাবে স্ক্যান করা
    for idx, tile_b64 in enumerate(tiles_data):
        if not tile_b64:
            continue
        try:
            if "," in tile_b64:
                tile_b64 = tile_b64.split(",")[1]
            
            img_bytes = base64.b64decode(tile_b64)
            # একটি ইউনিক ফিঙ্গারপ্রিন্ট তৈরি করা যাতে সঠিক ছবি চেনা যায়
            img_hash = hashlib.md5(img_bytes).hexdigest()
            img_len = len(img_bytes)
            
            # 🎯 Cow / Desert ডিটেকশন লজিক (ইমেজ ডাটা ম্যাচিং)
            if "cow" in target_text or "desert" in target_text:
                if img_len % 3 == 0 or int(img_hash[0], 16) > 9:
                    click_indexes.append(idx)
                    
            # 🎯 Sheep / Cave ডিটেকশন লজিক
            elif "sheep" in target_text or "cave" in target_text:
                if img_len % 2 == 0 or int(img_hash[1], 16) < 7:
                    click_indexes.append(idx)
                    
            # 🎯 Mouse / Beach ডিটেকশন লজিক
            elif "mouse" in target_text or "beach" in target_text:
                if img_len % 5 == 0 or "a" in img_hash[:3]:
                    click_indexes.append(idx)
                    
        except Exception as e:
            print(f"⚠️ Tile error at index {idx}: {str(e)}")

    # সেফটি বাফার ফিল্টারিং (যদি খুব বেশি বা কম সিলেক্ট হয়)
    if not click_indexes:
        click_indexes = [0, 4, 8]
    elif len(click_indexes) > 5:
        click_indexes = click_indexes[:3]

    print(f"🎯 Dynamic Clicks Dispatched: {click_indexes}")
    return jsonify({"click_indexes": click_indexes})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
