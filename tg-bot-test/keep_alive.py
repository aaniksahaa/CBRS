from flask import Flask, request
from threading import Thread

app = Flask(__name__)

# Global reference to the bot instance (passed from main.py)
bot_instance = None

# Default route
@app.route('/')
def index():
    return "Bot is alive!"

# Route to trigger a message
@app.route('/send_message', methods=['POST'])
async def send_message():
    chat_id = request.json.get('chat_id')
    message_text = request.json.get('message')
    
    if bot_instance and chat_id and message_text:
        await bot_instance.send_message(chat_id=chat_id, text=message_text)
        return f"Message sent to chat {chat_id}", 200
    else:
        return "Invalid request", 400

# Function to run the Flask server
def run():
    app.run(host='0.0.0.0', port=8080)

# Function to keep the Flask server alive
def keep_alive(bot):
    global bot_instance
    bot_instance = bot  # Set the bot instance for external use
    t = Thread(target=run)
    t.start()
