import os
import json
from flask import Flask, jsonify

app = Flask(__name__)


SCHEMA_DIR = "/data/schemas"

@app.route('/<app_name>', methods=['GET'])
def get_schema(app_name):
    filename = f"{os.path.basename(app_name)}.schema.json"
    file_path = os.path.join(SCHEMA_DIR, filename)

    print(f"[Schema] Request: {app_name}, Path: {file_path}")

    if not os.path.exists(file_path):
        return jsonify({"error": "Schema not found"}), 404

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)