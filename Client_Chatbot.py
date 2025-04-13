import requests

# URL of the Flask server's /chat endpoint
url = "http://127.0.0.1:9999/chat"

# Payload for the POST request
payload = {"message": "Hello and welcome to the party!"}
headers = {"Content-Type": "application/json"}

try:
    # Send POST request to the Flask server
    response = requests.post(url, json=payload, headers=headers)
    print(response.json())

    # Check the response status
    if response.status_code == 200:
        print("Chatbot Response:", response.json())
    else:
        print(f"Error {response.status_code}: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")