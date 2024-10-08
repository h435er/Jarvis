from flask import Flask, render_template, request, jsonify
import subprocess
import multiprocessing

app = Flask(__name__)

# Global list to store the last 5 messages
manager = multiprocessing.Manager()
last_five_messages = manager.list()

def process_query_sync(user_input):
    """Processes user input in a separate process."""
    jarvis_context = "You are Jarvis, the assistant. Respond as Jarvis.\n" + user_input
    command = ['ollama', 'run', 'myjarvis', jarvis_context]

    result = subprocess.run(command, capture_output=True, text=True)
    response = result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"

    # Store the message and response
    last_five_messages.append({"sender": "You", "text": user_input})
    last_five_messages.append({"sender": "Jarvis", "text": response})
    

    # Keep only the last 5 messages
    if len(last_five_messages) > 10:  # 5 pairs of messages (user + Jarvis)
        last_five_messages[:] = last_five_messages[-10:]

    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    user_input = request.json.get("message")
    response = process_query_sync(user_input)  # Directly call and return the response
    return jsonify({"response": response})

@app.route("/get_last_messages", methods=["GET"])
def get_last_messages():
    return jsonify(list(last_five_messages))

if __name__ == "__main__":
    app.run(debug=True)
