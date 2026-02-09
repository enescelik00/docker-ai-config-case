import requests
import json
import ast
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURATION ---
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
SCHEMA_URL = os.getenv("SCHEMA_URL", "http://localhost:5001")
VALUES_URL = os.getenv("VALUES_URL", "http://localhost:5002")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")

def clean_and_parse_json(raw_str):
    """
    Cleans the AI output and converts it into a Python object.
    Supports both JSON (true/false) and Python (True/False) boolean formats.
    """
    # 1. Remove Markdown code blocks
    text = raw_str.replace("```json", "").replace("```", "").strip()

    # 2. Extract content strictly between first { and last }
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]

    # 3. Remove comment lines (// ...)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if '//' in line:
            if 'http://' not in line and 'https://' not in line:
                line = line.split('//')[0]
        cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)

    # 4. Method A: Try standard JSON parsing
    try:
        return json.loads(text)
    except:
        pass 

    # 5. Method B: Try Python literal evaluation
    try:
        text_py = text.replace("true", "True").replace("false", "False").replace("null", "None")
        return ast.literal_eval(text_py)
    except Exception as e:
        print(f"Parse Error: {str(e)}\nData: {text[:200]}...")
        return None

def query_ollama(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.0} 
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        return response.json().get("response", "").strip()
    except Exception as e:
        print(f"Ollama Connection Error: {e}")
        return None

@app.route('/message', methods=['POST'])
def handle_message_jk():
    user_input = request.json.get("input", "")
    print(f"\n[Bot] User Input: {user_input}")

    # STEP 1: Application Identification
    identify_prompt = f"""
    Identify the application name from the sentence below (Options: chat, matchmaking, tournament).
    Reply ONLY with the application name as a single word.
    
    Sentence: "{user_input}"
    """
    app_name = query_ollama(identify_prompt)
    if not app_name: 
        return jsonify({"error": "AI did not respond"}), 500
    
    app_name = app_name.lower().replace(".", "").replace("'", "").replace('"', "").strip()
    if " " in app_name: app_name = app_name.split()[-1]
    print(f"[Bot] Identified App: {app_name}")

    # STEP 2: Fetch Data
    try:
        requests.get(f"{SCHEMA_URL}/{app_name}") 
        vals = requests.get(f"{VALUES_URL}/{app_name}").json()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch data for {app_name}: {str(e)}"}), 500

    # STEP 3: Update Logic (NÜKLEER PROMPT BURADA)
    update_prompt = f"""
    You are a strict JSON generator. You do not speak. You do not summarize.
    
    TASK: Update the 'Current JSON' based on the 'User Request'.
    
    User Request: "{user_input}"
    Current JSON: {json.dumps(vals)}

    STRICT RULES:
    1. Output the FULL, VALID JSON file. 
    2. DO NOT use ellipses (...) or abbreviations. Every single field must be present.
    3. DO NOT output comments or explanations.
    4. If you abbreviate, the system will crash. Return the whole content.
    """
    
    raw_response = query_ollama(update_prompt)
    
    result_json = clean_and_parse_json(raw_response)

    if result_json:
        return jsonify(result_json), 200
    else:
        # Hata durumunda debug verisini bas ki ne yaptığını görelim
        return jsonify({"error": "Formatting error", "debug": raw_response}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)