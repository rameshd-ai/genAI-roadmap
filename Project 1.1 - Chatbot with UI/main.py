import openai
import json
import os
import gradio as gr

# Load API Key
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
key_path = os.path.join(parent_dir, 'key.json')

with open(key_path) as f:
    key_data = json.load(f)

client = openai.OpenAI(api_key=key_data["openai_api_key"])

# Function to interact with OpenAI API
def ask_openai(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Gradio interface function
def send_message(user_input, chat_history):
    if not user_input.strip():
        return "", chat_history
    
    bot_response = ask_openai(user_input)
    
    # Append user and bot messages in the correct format
    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": bot_response})
    
    return "", chat_history

# Setup Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("### GenAI Chatbot 🚀")
    
    # Chat area for conversation, using 'messages' format
    chatbot = gr.Chatbot(type='messages', show_label=False)
    
    # User input area
    user_input = gr.Textbox(placeholder="Type your message...", label="Your message", interactive=True)
    
    # Button to send message
    send_button = gr.Button("Send")
    
    # Function binding
    send_button.click(fn=send_message, inputs=[user_input, chatbot], outputs=[user_input, chatbot])

# Launch the Gradio app
demo.launch(debug=True)
