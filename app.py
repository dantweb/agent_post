import os
import traceback
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from src.logger_service import get_logger
from src.message_repo import message_repo as msg_repo

load_dotenv()

app = Flask(__name__)
logger = get_logger("agent_post")
logger.info("Starting agent_post Flask app")

@app.route('/api/agentlife/messages/', methods=['POST'])
def get_public_messages():
    try:
        data_raw = request.json
        agents_of_user = data_raw.get('agents_of_user', [])
        logger.debug(f"Agents of user: {agents_of_user}")

        all_messages = msg_repo.get_messages_for_the_given_agents(agents_of_user)
        logger.debug(f"All messages fetched: {all_messages}")

        messages_json = [msg.to_dict() for msg in all_messages]
        return jsonify({"messages": messages_json}), 200

    except Exception as e:
        tb_str = traceback.format_exc()
        logger.error(f"Error fetching messages: {e}\n{tb_str}")
        return jsonify({"error": str(e)}), 500


# 🔥 Global error handler — catches any unhandled exceptions
@app.errorhandler(Exception)
def handle_unexpected_error(e):
    tb_str = traceback.format_exc()
    logger.error(f"Unhandled exception: {e}\n{tb_str}")
    return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
