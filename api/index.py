from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# URL файла с ключами на GitHub
GITHUB_KEYS_URL = "https://raw.githubusercontent.com/AnderoExploiter/SynY/refs/heads/main/assets/6Opsk56457K.json"  # Замените на ваш URL

def load_keys():
    response = requests.get(GITHUB_KEYS_URL)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Не удалось загрузить ключи с GitHub")

@app.route('/api/auth', methods=['POST'])
def authenticate():
    data = request.get_json()

    if 'key' not in data:
        return jsonify({"error": "Ключ не предоставлен"}), 400

    user_key = data['key']
    
    try:
        valid_keys = load_keys()  # Загружаем ключи из файла
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Проверяем, есть ли ключ в загруженных допустимых ключах
    if user_key in valid_keys:
        return jsonify(valid_keys[user_key]), 200
    else:
        return jsonify({"error": "Неверный ключ"}), 401

if __name__ == '__main__':
    app.run(debug=True)
