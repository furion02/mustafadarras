from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import google.generativeai as genai
import json
from dotenv import load_dotenv
import os
load_dotenv()  # Load variables from .env
api_key = os.getenv("API_KEY")
genai.configure(api_key=os.environ["API_KEY"])
    

# Define the path for the chat history JSON file
script_directory = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(script_directory, "chat_history.json")

# Load chat history from JSON file if it exists
chat_history = []
if os.path.exists(json_file_path):
    with open(json_file_path, "r") as json_file:
        chat_history = json.load(json_file)
        print("Chat history loaded.")

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="Your only object is to talk about Mustafa Darras in a sentence or two, start by talking about skills and experience when model is launched, 30 words max, try to sell yourself to get a job")

# Convert the loaded history to the expected format
formatted_history = []
for entry in chat_history:
    if entry['role'] in ['user', 'model']:
        formatted_history.append({"role": entry["role"], "parts": entry["message"]})

# Start a chat session with the loaded history
chat = model.start_chat(history=formatted_history)

app = Flask(__name__)
CORS(app)  # Apply CORS to allow requests from any origin
user_input = "Give me an Elevator Pitch about me Mustafa Darras in first person, make it extremely professional! Short and Concise make sure to mention achievements at work places. *Avoid Using Stars*. make sure 30 to 40 words ONLY for this elevator pitch. avoid using quotation marks."
@app.route('/initial_message', methods=['GET'])
def initial_message():
    try:
        # Send a request to the AI for the elevator pitch
        initial_message_response = chat.send_message(user_input)
        chat_history.append({"role": "model", "message": initial_message_response.text})

        # Save chat history to JSON file
        #with open(json_file_path, "w") as json_file:
           # json.dump(chat_history, json_file, indent=4)

        return jsonify({"response": initial_message_response.text})
    except Exception as e:
        return jsonify({"response": f"An error occurred: {str(e)}"}), 500

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"response": "Invalid input"}), 400

    # Send the message to the model and get the response
    try:
        response = chat.send_message(user_input)
        chat_history.append({"role": "user", "message": user_input})
        chat_history.append({"role": "model", "message": response.text})
        
        # Save chat history to JSON file
        with open(json_file_path, "w") as json_file:
            json.dump(chat_history, json_file, indent=4)

        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(port=5000)
