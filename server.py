from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "*"}})

# Load the DialoGPT model and tokenizer
model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Add a basic test route
@app.route('/')
def test():
    return "Server is running!"  # Check if the server is active

# Add a route to handle favicon requests
@app.route('/favicon.ico')
def no_favicon():
    return "", 204  # Respond with "No Content"

# Define the chat endpoint to handle both GET and POST requests
@app.route('/chat', methods=['POST'])
def chat():
    try:
        print("Chat endpoint accessed via POST.")
        print("Request data:", request.data)  # Log raw request data
        user_input = request.json.get('message')
        print("User input:", user_input)  # Log the extracted input

        if not user_input:
            return jsonify({"error": "Message field is required in JSON payload"}), 400

        # Tokenize and generate reply
        inputs = tokenizer.encode(user_input, return_tensors="pt")
        print("Tokenized input:", inputs)  # Log tokenized data
        reply_ids = model.generate(inputs, max_length=100, num_return_sequences=1)
        reply = tokenizer.decode(reply_ids[0], skip_special_tokens=True)
        print("Generated reply:", reply)  # Log generated reply

        return jsonify({"reply": reply})
    except Exception as e:
        print(f"Error during processing: {e}")  # Log any errors
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Run the Flask application with explicit host and port
    print("Starting Flask app on 127.0.0.1:9999...")  # Log the startup process
    app.run(debug=True, host="127.0.0.1", port=9999)