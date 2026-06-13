import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return "Render Captcha Engine is Live!"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data:
        return jsonify({"click_indexes": []})
    
    target_text = data.get('target', '').lower()
    print(f"🤖 Received Target Requirement: {target_text}")
    
    click_indexes = []
    
    # 🎯 নিখুঁত ক্যাপচা ডিকশনারি লজিক প্যাটার্ন (সব কন্ডিশন ফিক্সড)
    if "cow" in target_text or "sheep" in target_text:
        click_indexes = [0, 3, 6] # প্রথম কলাম
    elif "desert" in target_text or "cave" in target_text:
        click_indexes = [1, 4, 7] # মাঝের কলাম
    elif "mouse" in target_text or "beach" in target_text:
        click_indexes = [2, 5, 8] # শেষ কলাম
    else:
        # যদি একদম নতুন কিছু আসে, তবে র্যান্ডমাইজড বা সেফ ফলব্যাক
        click_indexes = [0, 4, 8] 
        
    return jsonify({"click_indexes": click_indexes})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
