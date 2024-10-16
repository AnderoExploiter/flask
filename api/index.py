from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# URL файла с ключами на GitHub
GITHUB_KEYS_URL = "https://raw.githubusercontent.com/AnderoExploiter/SynY/refs/heads/main/assets/6Opsk56457K.json"
GITHUB_REPO_URL = "https://github.com/AnderoExploiter/SynY"  # Замените на ваш URL репозитория

def load_keys():
    response = requests.get(GITHUB_KEYS_URL)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Не удалось загрузить ключи с GitHub")

def update_keys_on_github(keys):
    # Обновляем файл с ключами на GitHub
    headers = {
        'Authorization': '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',  # Замените на ваш токен
        'Content-Type': 'application/json'
    }
    
    # Получаем SHA файла для обновления
    response = requests.get(GITHUB_REPO_URL, headers=headers)
    if response.status_code == 200:
        sha = response.json()['sha']
        data = {
            "message": "Обновление ключей",
            "content": json.dumps(keys),
            "sha": sha
        }
        update_response = requests.put(GITHUB_REPO_URL, headers=headers, json=data)
        return update_response.status_code == 200
    else:
        raise Exception("Не удалось получить SHA файла на GitHub")

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
        user_data = valid_keys[user_key]
        
        # Определяем сообщение для конкретного пользователя
        message = f"Hello, {user_data['username']}! Your role is {user_data['role']}."

        return jsonify({
            "user_data": user_data,
            "message": message
        }), 200
    else:
        return jsonify({"error": "Неверный ключ"}), 401

@app.route('/api/keys/add', methods=['POST'])
def add_key():
    data = request.get_json()
    user_key = data.get('key')
    new_key = data.get('new_key')
    username = data.get('username')
    role = data.get('role')

    if not user_key or not new_key or not username or not role:
        return jsonify({"error": "Ключ, новый ключ, имя или роль не предоставлены"}), 400

    try:
        valid_keys = load_keys()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if user_key in valid_keys and valid_keys[user_key]['role'] == 'Owner':
        valid_keys[new_key] = {"username": username, "role": role}  # Добавляем новый ключ
        if update_keys_on_github(valid_keys):
            return jsonify({"message": "Ключ успешно добавлен!"}), 200
        else:
            return jsonify({"error": "Не удалось обновить ключи на GitHub"}), 500
    else:
        return jsonify({"error": "У вас нет прав для добавления ключей"}), 403

@app.route('/api/keys/delete', methods=['POST'])
def delete_key():
    data = request.get_json()
    user_key = data.get('key')
    key_to_delete = data.get('key_to_delete')

    if not user_key or not key_to_delete:
        return jsonify({"error": "Ключ или ключ для удаления не предоставлены"}), 400

    try:
        valid_keys = load_keys()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if user_key in valid_keys and valid_keys[user_key]['role'] == 'Owner':
        if key_to_delete in valid_keys:
            del valid_keys[key_to_delete]
            if update_keys_on_github(valid_keys):
                return jsonify({"message": "Ключ успешно удален!"}), 200
            else:
                return jsonify({"error": "Не удалось обновить ключи на GitHub"}), 500
        else:
            return jsonify({"error": "Ключ для удаления не найден"}), 404
    else:
        return jsonify({"error": "У вас нет прав для удаления ключей"}), 403

if __name__ == '__main__':
    app.run(debug=True)
