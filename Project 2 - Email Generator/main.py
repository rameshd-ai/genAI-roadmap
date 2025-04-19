import os
import json
import openai

# Path to key.json outside the project folder
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
key_path = os.path.join(parent_dir, 'key.json')

# Load API key
with open(key_path) as f:
    key_data = json.load(f)

# Initialize OpenAI client
client = openai.OpenAI(api_key=key_data["openai_api_key"])


def zero_shot_prompt(subject, tone):
    return f"""
You are a professional email copywriter.

Task: Based on the subject line provided, write a complete email.

Subject: {subject}
Tone: {tone}

Constraints:
- Keep the email clear and concise.
- Make sure it sounds natural and human-written.

Start writing the email now:
"""

def few_shot_prompt(subject, tone):
    return f"""
You are a professional email copywriter.

Here are some examples:

Example 1:
Subject: Apology for Late Delivery
Tone: Apologetic
Email:
Dear Customer,
We sincerely apologize for the delay in delivering your recent order. Unexpected circumstances caused a delay, and we are working hard to ensure it doesn’t happen again. Thank you for your patience.

Example 2:
Subject: Congratulations on Your Promotion
Tone: Warm
Email:
Dear [Recipient],
Congratulations on your well-deserved promotion! Your hard work and dedication have truly paid off. Wishing you continued success in your new role.

Now, based on the following details, write a new email:

Subject: {subject}
Tone: {tone}

Constraints:
- Keep the email clear and concise.
- Make it sound natural and human-written.

Begin:
"""

def chain_of_thought_prompt(subject, tone):
    return f"""
You are a professional email copywriter.

Task: Write an email based on the subject line and tone provided.

Steps to follow:
1. List the key points the email should cover.
2. Organize the points logically.
3. Draft the email.

Subject: {subject}
Tone: {tone}

Constraints:
- Keep it clear and concise.
- Ensure the email sounds human-written.

Begin:
"""

def generate_email(prompt, temperature=0.7, max_tokens=500):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content.strip()


def main():
    print("=== Smart Email Generator ===")
    subject = input("Enter the email subject: ")
    tone = input("Enter the email tone (Formal, Casual, Apologetic, etc.): ")

    print("\nChoose Prompt Style:")
    print("1. Zero-shot")
    print("2. Few-shot")
    print("3. Chain-of-thought")
    choice = input("Enter 1, 2, or 3: ")

    if choice == "1":
        prompt = zero_shot_prompt(subject, tone)
    elif choice == "2":
        prompt = few_shot_prompt(subject, tone)
    elif choice == "3":
        prompt = chain_of_thought_prompt(subject, tone)
    else:
        print("Invalid choice. Exiting.")
        return

    temp = float(input("Set creativity (temperature, e.g., 0.7): "))
    max_toks = int(input("Set max tokens for email length (e.g., 500): "))

    print("\nGenerating email...\n")
    email = generate_email(prompt, temperature=temp, max_tokens=max_toks)
    print(email)

if __name__ == "__main__":
    main()
