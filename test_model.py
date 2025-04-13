from transformers import AutoTokenizer, AutoModelForCausalLM

# Specify the DialoGPT model name
model_name = "microsoft/DialoGPT-medium"

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Assign pad_token_id explicitly to eos_token_id
tokenizer.pad_token = tokenizer.eos_token  # Set pad_token to eos_token
pad_token_id = tokenizer.eos_token_id      # Use eos_token_id for padding

# Test the model
user_input = "Hello, chatbot!"  # Example user input

# Tokenize the input
inputs = tokenizer.encode(user_input, return_tensors="pt")

# Create the attention mask
attention_mask = inputs.ne(pad_token_id)  # Compare against the explicitly assigned pad_token_id

# Generate a reply
reply_ids = model.generate(
    inputs,
    attention_mask=attention_mask,
    max_length=100,
    num_return_sequences=1,
    pad_token_id=pad_token_id  # Pass the pad_token_id explicitly
)

# Decode the response
reply = tokenizer.decode(reply_ids[0], skip_special_tokens=True)

# Print the chatbot's response
print("Generated reply:", reply)