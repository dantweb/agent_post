from flask import Flask, request, jsonify

app = Flask(__name__)

messages = []
from src.message_repo import message_repo as msg_repo

# New endpoint: /api/public/messages/
@app.route('/api/public/messages/', methods=['POST'])
def get_public_messages():
    try:
        agents_of_user = request.json.get('agents_of_user')
        all_messages = msg_repo.get_messages_for_the_given_agents(agents_of_user)
        messages_json = [msg.to_dict() for msg in all_messages]
        return jsonify({"messages": messages_json}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
