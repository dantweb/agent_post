from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage for messages
messages = []
from src.message_repo import message_repo as msg_repo

# New endpoint: /api/public/messages/
@app.route('/api/public/messages/', methods=['GET'])
def get_public_messages():
    try:
        all_messages = msg_repo.find_all()
        messages_json = [msg.to_dict() for msg in all_messages]
        return jsonify({"messages": messages_json}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
