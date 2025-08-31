from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage for messages
messages = []


@app.route('/test', methods=['GET', 'POST'])
def handle_messages():
    if request.method == 'POST':
        return jsonify({"message": "post request ok"}), 201
    elif request.method == 'GET':
        return jsonify({"messages": "get request is ok"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
