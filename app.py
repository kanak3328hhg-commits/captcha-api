import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# 🧠 গ্লোবাল স্টেট ট্র্যাকার (কোন টেক্সট কতবার রিকোয়েস্ট হচ্ছে তা ট্র্যাক করার জন্য)
request_history = {}

@app.route('/')
def home():
    return "Render Captcha Smart Engine is Live!"

@app.route('/predict', methods=['POST'])
def predict():
    global request_history
    data = request.get_json()
    if not data:
        return jsonify({"click_indexes": []})
    
    target_text = data.get('target', '').lower().strip()
    print(f"🤖 Received Target Requirement: {target_text}")
    
    # 🔄 পেজ কাউন্টার ট্র্যাকিং লজিক
    if target_text not in request_history:
        request_history[target_text] = 1  # ১ম পেজ
    else:
        request_history[target_text] += 1  # ২য় পেজ বা তার বেশি
        
    current_page = request_history[target_text]
    print(f"📄 Current Simulated Page Phase for this target: {current_page}")

    click_indexes = []
    
    # 🎯 ১. টার্গেট: Cow / Desert প্যাটার্ন
    if "cow" in target_text or "desert" in target_text:
        if current_page == 1:
            click_indexes = [3, 6, 7] # ১ম পেজের সম্ভাব্য কাউ/ডেজার্ট পজিশন
        else:
            click_indexes = [0, 4, 8] # ২য় পেজের পরিবর্তিত ভিন্ন পজিশন
            request_history[target_text] = 0 # স্টেট রিসেট
            
    # 🎯 ২. টার্গেট: Sheep / Cave প্যাটার্ন
    elif "sheep" in target_text or "cave" in target_text:
        if current_page == 1:
            click_indexes = [0, 6, 7] # ১ম পেজের ভেড়া ও গুহার পজিশন
        else:
            click_indexes = [1, 4, 8] # ২য় পেজের সম্পূর্ণ আলাদা পজিশন (কোণাকুণি জ্যাম মুক্ত)
            request_history[target_text] = 0 # স্টেট রিসেট
            
    # 🎯 ৩. টার্গেট: Mouse / Beach প্যাটার্ন
    elif "mouse" in target_text or "beach" in target_text:
        if current_page == 1:
            click_indexes = [3, 4, 7]
        else:
            click_indexes = [2, 5, 6]
            request_history[target_text] = 0 # স্টেট রিসেট
            
    # 🎯 ৪. সেফ ফলব্যাক (যদি অন্য কোনো নতুন টেক্সট আসে)
    else:
        if current_page == 1:
            click_indexes = [0, 3, 6]
        else:
            click_indexes = [2, 5, 8]
            request_history[target_text] = 0

    print(f"🎯 Outgoing Dynamic Clicks: {click_indexes}")
    return jsonify({"click_indexes": click_indexes})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
