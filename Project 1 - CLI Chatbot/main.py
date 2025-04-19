import openai
import json
import os

# Path to key.json outside the project folder
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
key_path = os.path.join(parent_dir, 'key.json')

# Load API key
with open(key_path) as f:
    key_data = json.load(f)

client = openai.OpenAI(api_key=key_data["openai_api_key"])

def ask_openai(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def main():
    print("Welcome to your CLI Chatbot! Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        answer = ask_openai(user_input)
        print("Bot:", answer)

if __name__ == "__main__":
    main()
