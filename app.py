import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# রেন্ডার সার্ভার থেকে ব্রাউজার এক্সটেনশনে ডাটা আদান-প্রদানের সিকিউরিটি ওপেন করা হলো
CORS(app, resources={r"/*": {"origins": "*"}}) 

@app.route('/')
def home():
    return "Render Captcha DOM Engine is Live and Running!"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data:
        return jsonify({"click_indexes": []})
    
    target_text = data.get('target', '').lower()
    print(f"🤖 Received Target Requirement: {target_text}")
    
    click_indexes = []
    
    # ক্যাপচার রুলস অ্যানালাইসিস প্যাটার্ন
    if "cow" in target_text or "sheep" in target_text:
        click_indexes = [0, 3, 6]
    elif "desert" in target_text or "cave" in target_text:
        click_indexes = [1, 4, 7]
    else:
        click_indexes = [0, 2, 4, 6, 8] # সেফ ফলব্যাক জেনারেটর
        
    return jsonify({"click_indexes": click_indexes})

if __name__ == '__main__':
    # রেন্ডার ডট কমের এনভায়রনমেন্ট পোর্ট ডিটেকশন ফিক্স
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
