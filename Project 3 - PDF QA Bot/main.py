import os
import json
import hashlib
import streamlit as st
from pdf_loader import load_and_split_pdf
from embedder import create_or_load_vector_store
from qa_engine import create_qa_chain
from utils import export_to_pdf, export_to_text
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings  # <-- You forgot to import this earlier

# Set page config at the very top, before any other Streamlit commands
st.set_page_config(page_title="📄 AI PDF Q&A Bot", page_icon=":guardsman:", layout="wide")

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
        # Process multiple PDFs
        all_docs = []
        for uploaded_file in uploaded_files:
            pdf_path = os.path.join("docs", uploaded_file.name)
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Process each PDF and store its vector store
            pdf_name = os.path.splitext(uploaded_file.name)[0]
            store_path = os.path.join("store", pdf_name)

            docs = load_and_split_pdf(pdf_path)
            all_docs.extend(docs)  # <-- Store *documents*, not vectorstore

        # Create one FAISS index from all documents
        embeddings = OpenAIEmbeddings()
        combined_vector_store = FAISS.from_documents(all_docs, embeddings)

        # Create QA chain using combined vector store
        qa_chain = create_qa_chain(combined_vector_store)

        # Allow users to ask questions
        query = st.text_input("Ask your question:")

        if query:
            response = qa_chain.run(query)
            st.write("### Answer:")
            st.write(response)

            # Store conversation in session state for persistent memory
            if 'conversation' not in st.session_state:
                st.session_state.conversation = []

            # Only append if the same question doesn't exist in session state
            existing_questions = [conv['question'] for conv in st.session_state.conversation]
            if query not in existing_questions:
                st.session_state.conversation.append({"question": query, "answer": response})
            
            # Option to export answers
            if st.button("Export Q&A to PDF"):
                export_to_pdf(st.session_state.conversation)

            if st.button("Export Q&A to Text"):
                export_to_text(st.session_state.conversation)

if __name__ == "__main__":
    main()
