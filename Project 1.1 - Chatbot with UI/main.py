import tkinter as tk
import openai
import json
import os

# Load API Key
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
key_path = os.path.join(parent_dir, 'key.json')

with open(key_path) as f:
    key_data = json.load(f)

client = openai.OpenAI(api_key=key_data["openai_api_key"])

def ask_openai(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def send_message(event=None):
    user_input = entry.get()
    if not user_input.strip():
        return
    
    create_message_bubble(user_input, "user")
    entry.delete(0, tk.END)

    bot_response = ask_openai(user_input)
    create_message_bubble(bot_response, "bot")

def create_message_bubble(message, sender_type):
    outer_frame = tk.Frame(chat_area_frame, bg="#f0f0f0")
    outer_frame.pack(fill="x", pady=5, padx=10)

    inner_frame = tk.Frame(outer_frame, bg="#f0f0f0")
    inner_frame.pack(fill="both")

    bubble_color = "#DCF8C6" if sender_type == "user" else "#FFFFFF"
    justify_dir = "right" if sender_type == "user" else "left"

    message_frame = tk.Frame(inner_frame, bg="#f0f0f0")
    message_frame.pack(
        side="right" if sender_type == "user" else "left",
        anchor="e" if sender_type == "user" else "w",
        padx=(100, 10) if sender_type == "user" else (10, 100),
        pady=5
    )

    bubble = tk.Label(
        message_frame,
        text=message,
        bg=bubble_color,
        fg="black",
        font=("Arial", 12),
        wraplength=500,
        justify=justify_dir,
        padx=12,
        pady=8,
        bd=1,
        relief="solid"
    )
    bubble.pack(side="left" if sender_type == "bot" else "right", padx=5)

    if sender_type == "bot":
        copy_button = tk.Button(
            message_frame,
            text="📋",
            font=("Arial", 10),
            command=lambda: copy_to_clipboard(message),
            bg="#f0f0f0",
            relief="flat",
            cursor="hand2"
        )
        copy_button.pack(side="right", padx=5)

    chat_canvas.update_idletasks()
    chat_canvas.yview_moveto(1.0)

def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()

# Main Window
root = tk.Tk()
root.title("GenAI Chatbot 🚀")

root.geometry("700x800")
root.configure(bg="#f0f0f0")

# Chat Area with Scroll
chat_frame = tk.Frame(root, bg="#f0f0f0")
chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

chat_canvas = tk.Canvas(chat_frame, bg="#f0f0f0", highlightthickness=0)
chat_scrollbar = tk.Scrollbar(chat_frame, orient="vertical", command=chat_canvas.yview)
chat_area_frame = tk.Frame(chat_canvas, bg="#f0f0f0")

chat_area_frame.bind(
    "<Configure>",
    lambda e: chat_canvas.configure(
        scrollregion=chat_canvas.bbox("all")
    )
)

chat_canvas.create_window((0, 0), window=chat_area_frame, anchor="nw")
chat_canvas.configure(yscrollcommand=chat_scrollbar.set)

chat_canvas.pack(side="left", fill="both", expand=True)
chat_scrollbar.pack(side="right", fill="y")

# Input Area
entry_frame = tk.Frame(root, bg="#f0f0f0")
entry_frame.pack(pady=10, fill=tk.X)

entry = tk.Entry(entry_frame, font=("Arial", 14))
entry.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
entry.bind("<Return>", send_message)

send_button = tk.Button(entry_frame, text="Send", command=send_message, font=("Arial", 12), bg="#4CAF50", fg="white")
send_button.pack(side=tk.RIGHT, padx=10)

root.mainloop()
import tkinter as tk
import openai
import json
import os

# Load API Key
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
key_path = os.path.join(parent_dir, 'key.json')

with open(key_path) as f:
    key_data = json.load(f)

client = openai.OpenAI(api_key=key_data["openai_api_key"])

def ask_openai(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def send_message(event=None):
    user_input = entry.get()
    if not user_input.strip():
        return
    
    create_message_bubble(user_input, "user")
    entry.delete(0, tk.END)

    bot_response = ask_openai(user_input)
    create_message_bubble(bot_response, "bot")

def create_message_bubble(message, sender_type):
    outer_frame = tk.Frame(chat_area_frame, bg="#f0f0f0")
    outer_frame.pack(fill="x", pady=5, padx=10)

    inner_frame = tk.Frame(outer_frame, bg="#f0f0f0")
    inner_frame.pack(fill="both")

    bubble_color = "#DCF8C6" if sender_type == "user" else "#FFFFFF"
    justify_dir = "right" if sender_type == "user" else "left"

    message_frame = tk.Frame(inner_frame, bg="#f0f0f0")
    message_frame.pack(
        side="right" if sender_type == "user" else "left",
        anchor="e" if sender_type == "user" else "w",
        padx=(100, 10) if sender_type == "user" else (10, 100),
        pady=5
    )

    bubble = tk.Label(
        message_frame,
        text=message,
        bg=bubble_color,
        fg="black",
        font=("Arial", 12),
        wraplength=500,
        justify=justify_dir,
        padx=12,
        pady=8,
        bd=1,
        relief="solid"
    )
    bubble.pack(side="left" if sender_type == "bot" else "right", padx=5)

    if sender_type == "bot":
        copy_button = tk.Button(
            message_frame,
            text="📋",
            font=("Arial", 10),
            command=lambda: copy_to_clipboard(message),
            bg="#f0f0f0",
            relief="flat",
            cursor="hand2"
        )
        copy_button.pack(side="right", padx=5)

    chat_canvas.update_idletasks()
    chat_canvas.yview_moveto(1.0)

def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()

# Main Window
root = tk.Tk()
root.title("GenAI Chatbot 🚀")

root.geometry("700x800")
root.configure(bg="#f0f0f0")

# Chat Area with Scroll
chat_frame = tk.Frame(root, bg="#f0f0f0")
chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

chat_canvas = tk.Canvas(chat_frame, bg="#f0f0f0", highlightthickness=0)
chat_scrollbar = tk.Scrollbar(chat_frame, orient="vertical", command=chat_canvas.yview)
chat_area_frame = tk.Frame(chat_canvas, bg="#f0f0f0")

chat_area_frame.bind(
    "<Configure>",
    lambda e: chat_canvas.configure(
        scrollregion=chat_canvas.bbox("all")
    )
)

chat_canvas.create_window((0, 0), window=chat_area_frame, anchor="nw")
chat_canvas.configure(yscrollcommand=chat_scrollbar.set)

chat_canvas.pack(side="left", fill="both", expand=True)
chat_scrollbar.pack(side="right", fill="y")

# Input Area
entry_frame = tk.Frame(root, bg="#f0f0f0")
entry_frame.pack(pady=10, fill=tk.X)

entry = tk.Entry(entry_frame, font=("Arial", 14))
entry.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
entry.bind("<Return>", send_message)

send_button = tk.Button(entry_frame, text="Send", command=send_message, font=("Arial", 12), bg="#4CAF50", fg="white")
send_button.pack(side=tk.RIGHT, padx=10)

root.mainloop()

