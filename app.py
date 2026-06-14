# ========================================================
# পাইথন ব্যাকএন্ড: app.py (গুগল জেমিনি ফিক্সড সংস্করণ)
# ========================================================

import os
import requests
import re
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# লগিং কনফিগারেশন
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON payload", "click_indexes": []}), 400
            
        img_b64 = data.get('full_grid')
        target = data.get('target', 'object')
        
        if isinstance(target, str):
            target = target.strip()
        
        if not img_b64:
            return jsonify({"error": "Missing full_grid image data", "click_indexes": []}), 400

        # Render-এর Environment Variable থেকে Gemini API Key নেওয়া
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            logger.error("GEMINI_API_KEY Environment Variable missing in Render!")
            return jsonify({"error": "Missing API Key Configuration", "click_indexes": []}), 500

        # 🎯 ফিক্স ১: সঠিক মডেল নেম 'gemini-1.5-flash' ব্যবহার করা হয়েছে
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        prompt_text = (
            f"This image is a 3x3 grid of tiles indexed from 0 to 8 (0=top-left, 8=bottom-right). "
            f"Identify the index numbers of all tiles that contain a '{target}'. "
            f"Your output must ONLY contain the numbers inside square brackets, for example: [1, 4, 7]. "
            f"If no tiles contain the target, return []. Do not include any reasoning or extra text."
        )

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt_text},
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": img_b64
                        }
                    }
                ]
            }]
        }
        
        headers = {'Content-Type': 'application/json'}
        
        logger.info(f"Sending request to Google Gemini (1.5-Flash). Target: {target}")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            res_json = response.json()
            
            # 🎯 ফিক্স ২: KeyError এড়াতে 'candidates' কি-টি নিরাপদে চেক করা হচ্ছে
            if 'candidates' in res_json and len(res_json['candidates']) > 0:
                try:
                    ai_response = res_json['candidates'][0]['content']['parts'][0]['text']
                    logger.info(f"Gemini Raw Response: {ai_response}")
                    
                    # স্কয়ার ব্র্যাকেটের ভেতরের সংখ্যাগুলো পার্স করা
                    bracket_match = re.search(r'\[(.*?)\]', ai_response)
                    if bracket_match:
                        inside_content = bracket_match.group(1)
                        found_indexes = [int(x) for x in re.findall(r'[0-8]', inside_content)]
                    else:
                        found_indexes = [int(x) for x in re.findall(r'[0-8]', ai_response)]
                        
                    click_indexes = sorted(list(set(found_indexes)))
                    logger.info(f"Final Filtered Click Indexes: {click_indexes}")
                    return jsonify({"click_indexes": click_indexes})
                    
                except Exception as parse_err:
                    logger.error(f"Parsing error: {str(parse_err)}. Response was: {res_json}")
                    return jsonify({"error": "Failed to parse AI structure", "click_indexes": []}), 502
            else:
                # যদি জেমিনি কোনো ইন্টারনাল এরর মেসেজ দেয়, তা লগে প্রিন্ট হবে
                logger.error(f"Gemini returned 200 but contains error/block: {res_json}")
                return jsonify({"error": "No response candidates returned", "details": res_json, "click_indexes": []}), 502
        else:
            # এপিআই কী ভুল হলে বা অন্য কোনো সমস্যা হলে এখানে আসল এররটি দেখা যাবে
            logger.error(f"Gemini API Error {response.status_code}: {response.text}")
            return jsonify({
                "error": f"Gemini API Code {response.status_code}",
                "details": response.text,
                "click_indexes": []
            }), 502
            
    except Exception as e:
        logger.error(f"Unexpected internal server error: {str(e)}")
        return jsonify({"error": str(e), "click_indexes": []}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
