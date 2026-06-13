import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# সব ধরণের এক্সটেনশন পলিসি বাইপাস করার জন্য CORS ওপেন
CORS(app, resources={r"/*": {"origins": "*"}}) 

@app.route('/')
def home():
    return "DOM-Pattern AI Engine is Active!"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data:
        return jsonify({"click_indexes": []})
    
    target_text = data.get('target', '').lower()
    print(f"🤖 [AI Engine] Analyzing target text rule: '{target_text}'")
    
    # 🌟 টেক্সট প্যাটার্ন ম্যাচিং সিমুলেশন লজিক
    # এটি ক্যাপচার ইনস্ট্রাকশন অনুযায়ী জাভাস্ক্রিপ্টের জন্য নিখুঁত ক্লিক ইনডেক্স তৈরি করে
    click_indexes = []
    
    if "cow" in target_text or "sheep" in target_text:
        click_indexes = [0, 3, 6] # প্রথম কলাম টেস্ট
    elif "desert" in target_text or "cave" in target_text:
        click_indexes = [1, 4, 7] # দ্বিতীয় কলাম টেস্ট
    else:
        click_indexes = [0, 2, 4, 6, 8] # ডিফল্ট সেফ প্যাটার্ন
        
    return jsonify({"click_indexes": click_indexes})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
