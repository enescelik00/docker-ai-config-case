import os
import json
from flask import Flask, jsonify

app = Flask(__name__)


VALUES_DIR = "/data/values"

@app.route('/<app_name>', methods=['GET'])
def get_values(app_name):
    filename = f"{os.path.basename(app_name)}.value.json"
    file_path = os.path.join(VALUES_DIR, filename)

    print(f"[Values] Request: {app_name}, Path: {file_path}")

    if not os.path.exists(file_path):
        return jsonify({"error": "Values not found"}), 404

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)