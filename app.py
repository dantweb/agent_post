from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage for messages
messages = []


@app.route('/messages', methods=['GET', 'POST'])
def handle_messages():
    if request.method == 'POST':
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "Invalid input, 'message' key is required"}), 400
        messages.append(data['message'])
        return jsonify({"message": "Message added successfully!"}), 201
    elif request.method == 'GET':
        return jsonify({"messages": messages}), 200
    else:
        return jsonify({"error": "Invalid request method"}), 405


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
