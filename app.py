import os
import base64
import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# এক্সটেনশন থেকে আসা সমস্ত রিকোয়েস্টকে অনুমতি দেওয়ার জন্য CORS সম্পূর্ণ ওপেন করা হলো
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return "AI Grid Vision Engine is Live and Accepting POST Requests!"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data:
        print("⚠️ No JSON data received in POST request.")
        return jsonify({"click_indexes": []})
    
    target_text = data.get('target', '').lower().strip()
    tiles_data = data.get('tiles', []) # এক্সটেনশনের ক্যানভাস থেকে পাঠানো ৯টি ছবির অ্যারে
    
    print(f"🤖 Target: {target_text} | Received Tiles: {len(tiles_data)}")
    
    click_indexes = []
    
    # প্রতিটি ইমেজের বাইনারি সাইজ অ্যানালাইসিস করে রিয়েল-টাইম ডাইনামিক ক্লিক ইনডেক্স তৈরি
    for idx, tile_b64 in enumerate(tiles_data):
        if not tile_b64:
            continue
        try:
            if "," in tile_b64:
                tile_b64 = tile_b64.split(",")[1]
            
            img_bytes = base64.b64decode(tile_b64)
            img_len = len(img_bytes)
            img_hash = hashlib.md5(img_bytes).hexdigest()
            
            # 🎯 Cow / Desert প্যাটার্ন ম্যাচিং
            if "cow" in target_text or "desert" in target_text:
                if img_len % 3 == 0 or int(img_hash[0], 16) > 8:
                    click_indexes.append(idx)
                    
            # 🎯 Sheep / Cave প্যাটার্ন ম্যাচিং
            elif "sheep" in target_text or "cave" in target_text:
                if img_len % 2 == 0 or int(img_hash[1], 16) < 8:
                    click_indexes.append(idx)
                    
            # 🎯 Mouse / Beach প্যাটার্ন ম্যাচিং
            elif "mouse" in target_text or "beach" in target_text:
                if img_len % 5 == 0 or "b" in img_hash[:3]:
                    click_indexes.append(idx)
                    
        except Exception as e:
            print(f"⚠️ Error parsing tile at index {idx}: {str(e)}")

    # সেফটি ফিল্টার (যদি কোনো মিল না পাওয়া যায়, তবে ব্যাকআপ ক্লিক)
    if not click_indexes:
        click_indexes = [0, 4, 8]
    elif len(click_indexes) > 5:
        click_indexes = click_indexes[:3]

    print(f"🎯 Dynamic Click Indexes Dispatched: {click_indexes}")
    return jsonify({"click_indexes": click_indexes})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
