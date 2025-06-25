import os
import json
import sys
import subprocess
import streamlit as st
from pdf_loader import load_and_split_pdf
from embedder import create_or_load_vector_store
from qa_engine import create_qa_chain
from utils import export_to_pdf, export_to_text
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings  # Correct import

# Set page config at the very top
st.set_page_config(page_title="📄 AI PDF Q&A Bot", page_icon=":guardsman:", layout="wide")

# Prevent Streamlit from crashing on torch dynamic class inspection
sys.modules['torch.classes'] = None

# Load OpenAI API Key from key.json
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
key_path = os.path.join(parent_dir, 'key.json')

with open(key_path) as f:
    key_data = json.load(f)

os.environ["OPENAI_API_KEY"] = key_data["openai_api_key"]

# Create folders if not exist
os.makedirs("docs", exist_ok=True)
os.makedirs("store", exist_ok=True)

def main():
    st.title("📄 AI PDF Q&A Bot")
    st.write("Upload multiple PDFs, ask questions, and get answers.")

    uploaded_files = st.file_uploader("Choose PDFs", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        all_vectorstores = []

        for uploaded_file in uploaded_files:
            pdf_path = os.path.join("docs", uploaded_file.name)
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            pdf_name = os.path.splitext(uploaded_file.name)[0]
            store_path = os.path.join("store", pdf_name)

            docs = load_and_split_pdf(pdf_path)

            # Create or load vectorstore for each PDF
            vectorstore = create_or_load_vector_store(docs, store_path, pdf_path)
            all_vectorstores.append(vectorstore)

        # Merge all vector stores into one
        if len(all_vectorstores) == 1:
            combined_vectorstore = all_vectorstores[0]
        else:
            combined_vectorstore = all_vectorstores[0]
            for vectorstore in all_vectorstores[1:]:
                combined_vectorstore.merge_from(vectorstore)

        # Create QA chain
        qa_chain = create_qa_chain(combined_vectorstore)

        # Allow user to ask questions
        query = st.text_input("Ask your question:")

        if query:
            response = qa_chain.run(query)
            st.write("### Answer:")
            st.write(response)

            # Store conversation in session state
            if 'conversation' not in st.session_state:
                st.session_state.conversation = []

            # Only append if the same question doesn't exist in session
            existing_questions = [conv['question'] for conv in st.session_state.conversation]
            if query not in existing_questions:
                st.session_state.conversation.append({"question": query, "answer": response})

            # Export options
            if st.button("Export Q&A to PDF"):
                export_to_pdf(st.session_state.conversation)

            if st.button("Export Q&A to Text"):
                export_to_text(st.session_state.conversation)

if __name__ == "__main__":
    main()
