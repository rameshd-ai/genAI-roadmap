import os
import json
import openai
import gradio as gr
from docx import Document

# Load OpenAI API Key
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
key_path = os.path.join(parent_dir, 'key.json')

with open(key_path) as f:
    key_data = json.load(f)

client = openai.OpenAI(api_key=key_data["openai_api_key"])

# Login Credentials
USERNAME = "admin"
PASSWORD = "password123"

# Prompt templates
def zero_shot_prompt(content_type, business_name, business_description, tone, seo_keywords):
    seo_part = f"\nSEO Keywords: {seo_keywords}" if seo_keywords else ""
    return f"""You are a professional website content writer.

Task: Create {content_type} content.

Business Name: {business_name}
Business Description: {business_description}
Tone: {tone}
{seo_part}

Constraints:
- Clear, engaging, audience-focused
- Natural SEO keywords, not stuffed
"""

def few_shot_prompt(content_type, business_name, business_description, tone, seo_keywords):
    seo_part = f"\nSEO Keywords: {seo_keywords}" if seo_keywords else ""
    return f"""You are a professional website content writer.

Examples:

Example 1:
Content Type: Home Page
Business: FreshBites (Organic Food Delivery)
Tone: Friendly
Content:
Welcome to FreshBites! We deliver fresh, organic produce straight to your door. Simple, healthy, and delicious — just the way nature intended.

Example 2:
Content Type: About Us
Business: CodeCrafters (Software Development)
Tone: Professional
Content:
At CodeCrafters, we engineer digital solutions that drive business success. Innovation, quality, and trust are the core of our work.

Now, create a new content piece:

Content Type: {content_type}
Business Name: {business_name}
Business Description: {business_description}
Tone: {tone}
{seo_part}
"""

def chain_of_thought_prompt(content_type, business_name, business_description, tone, seo_keywords):
    seo_part = f"\nSEO Keywords: {seo_keywords}" if seo_keywords else ""
    return f"""You are a professional website content writer.

Steps:
1. Understand the business and its audience.
2. Identify key messages.
3. Organize logically.
4. Write compelling {content_type} content.

Business Name: {business_name}
Business Description: {business_description}
Tone: {tone}
{seo_part}
"""

# Generate catchy Title
def generate_title(business_description):
    prompt = f"""Create a short, catchy website page title based on this business description:
"{business_description}"
Title:"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert website content strategist."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=20,
        top_p=1,
    )
    title = response.choices[0].message.content.strip()
    return title

# Suggest SEO Keywords
def suggest_seo_keywords(business_description):
    prompt = f"""Suggest 5 SEO keywords based on the following business description:
"{business_description}"
Return the keywords separated by commas."""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert SEO strategist."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=60,
        top_p=1,
    )
    keywords = response.choices[0].message.content.strip()
    return keywords

# Generate Content
def generate_content(content_type, business_name, business_description, tone, prompt_style, temperature, max_tokens, num_variations, seo_keywords):
    if not seo_keywords:
        seo_keywords = suggest_seo_keywords(business_description)

    if prompt_style == "Zero-shot":
        base_prompt = zero_shot_prompt(content_type, business_name, business_description, tone, seo_keywords)
    elif prompt_style == "Few-shot":
        base_prompt = few_shot_prompt(content_type, business_name, business_description, tone, seo_keywords)
    else:
        base_prompt = chain_of_thought_prompt(content_type, business_name, business_description, tone, seo_keywords)
    
    outputs = []
    for _ in range(num_variations):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant skilled at writing website content."},
                {"role": "user", "content": base_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        content = response.choices[0].message.content.strip()
        outputs.append(content)

    return "\n\n---\n\n".join(outputs)

# Save as txt
def save_txt(content):
    filename = "generated_content.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

# Save as docx
def save_docx(content):
    doc = Document()
    doc.add_paragraph(content)
    filename = "generated_content.docx"
    doc.save(filename)
    return filename

# Main App Function
def app(content_type, business_name, business_description, tone, prompt_style, temperature, max_tokens, num_variations, seo_keywords):
    auto_title = generate_title(business_description)
    generated_content = generate_content(content_type, business_name, business_description, tone, prompt_style, temperature, max_tokens, num_variations, seo_keywords)
    full_content = f"### {auto_title}\n\n{generated_content}"
    txt_path = save_txt(full_content)
    docx_path = save_docx(full_content)
    return auto_title, full_content, txt_path, docx_path

# Authenticate user
def authenticate(username, password):
    if username == USERNAME and password == PASSWORD:
        return gr.update(visible=False), gr.update(visible=True), ""
    else:
        return gr.update(visible=True), gr.update(visible=False), "❌ Invalid credentials. Please try again."

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# 🔒 Login to access Website Content Creator Tool")

    # Login Form
    with gr.Group() as login_block:
        username = gr.Textbox(label="Username", placeholder="Enter username")
        password = gr.Textbox(label="Password", placeholder="Enter password", type="password")
        login_btn = gr.Button("Login")
        login_msg = gr.Label(visible=True)

    # Main App (hidden initially)
    with gr.Group(visible=False) as main_app:
        gr.Markdown("# 🌟 Website Content Creator Tool 2.2")
        gr.Markdown("🚀 Generate high-quality website content with auto Title, auto SEO suggestions, 📄 Docx & Text Export!")

        with gr.Row():
            content_type = gr.Dropdown(["Home Page", "About Us", "Services", "Product Description", "Blog Post"], label="Content Type", value="Home Page")
            tone = gr.Dropdown(["Formal", "Friendly", "Professional", "Casual", "Luxury"], label="Tone", value="Friendly")
            prompt_style = gr.Radio(["Zero-shot", "Few-shot", "Chain-of-thought"], label="Prompt Style", value="Zero-shot")

        business_name = gr.Textbox(label="Business Name", placeholder="e.g., Aura Creations")
        business_description = gr.Textbox(label="Business Description", placeholder="e.g., Aura Creations offers handmade home decor and personalized gifts...")
        seo_keywords = gr.Textbox(label="SEO Keywords (optional)", placeholder="Leave empty to auto-generate")

        with gr.Row():
            temperature = gr.Slider(minimum=0.0, maximum=1.0, value=0.7, label="Creativity (Temperature)")
            max_tokens = gr.Slider(minimum=100, maximum=1500, value=700, label="Max Tokens (Content Length)")
            num_variations = gr.Slider(minimum=1, maximum=5, step=1, value=1, label="Number of Variations")

        generate_button = gr.Button("✨ Generate Content")
        title_output = gr.Textbox(label="Auto-Generated Title")
        output = gr.Textbox(lines=20, label="Generated Content", interactive=True)

        with gr.Row():
            download_txt_button = gr.File(label="Download as .txt")
            download_docx_button = gr.File(label="Download as .docx")

        generate_button.click(app, 
            inputs=[content_type, business_name, business_description, tone, prompt_style, temperature, max_tokens, num_variations, seo_keywords],
            outputs=[title_output, output, download_txt_button, download_docx_button])

    # Connect login button
    login_btn.click(authenticate, inputs=[username, password], outputs=[login_block, main_app, login_msg])

demo.launch(debug=True)
