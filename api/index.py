from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# URL файла с ключами на GitHub
GITHUB_KEYS_URL = "https://raw.githubusercontent.com/AnderoExploiter/SynY/refs/heads/main/assets/6Opsk56457K.json"

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
        user_data = valid_keys[user_key]
        
        # Определяем сообщение для конкретного пользователя
        if user_data['username'] == "Tim":
            message = "Welcome, " + user_data['role'] + " Tim!"
        elif user_data['username'] == "SrFox":
            message = "Welcome, " + user_data['role'] + " SrFox!"
        else:
            message = "Hello, " + user_data['username'] + "!"

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

    if not user_key or not new_key:
        return jsonify({"error": "Ключ или новый ключ не предоставлены"}), 400

    try:
        valid_keys = load_keys()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if user_key in valid_keys and valid_keys[user_key]['role'] == 'Owner':
        valid_keys[new_key] = {"username": "NewUser", "role": "User"}  # Пример добавления нового ключа
        return jsonify({"message": "Ключ успешно добавлен!"}), 200
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
            return jsonify({"message": "Ключ успешно удален!"}), 200
        else:
            return jsonify({"error": "Ключ для удаления не найден"}), 404
    else:
        return jsonify({"error": "У вас нет прав для удаления ключей"}), 403

if __name__ == '__main__':
    app.run(debug=True)