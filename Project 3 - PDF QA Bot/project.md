Absolutely! Here's a **full project documentation** for your AI-powered PDF Q&A Bot, including the entire workflow, installation steps, and code breakdown.

---

# 📄 **AI PDF Q&A Bot** - Project Documentation

## 1. **Overview**

This project is a **PDF Question & Answer Bot** that:
- Uploads PDFs.
- Processes the content (embedding it into a vector store).
- Allows users to ask questions about the PDF content.
- Uses **OpenAI API** and **LangChain** to perform semantic search and generate answers.
- Saves the vector embeddings (FAISS index) and prevents unnecessary reprocessing by detecting changes in PDF content.

---

## 2. **Technologies Used**
- **LangChain**: For document processing and semantic search.
- **FAISS**: For storing and querying vector embeddings.
- **OpenAI Embeddings**: For generating vector embeddings from text.
- **Streamlit**: For the user interface.
- **PyPDF2**: For PDF parsing and extraction.

---

## 3. **Project Structure**

```
your_project/
│
├── main.py            # Main Streamlit application
├── pdf_loader.py      # PDF loading and splitting logic
├── embedder.py        # FAISS vector store management
├── qa_engine.py       # Question answering chain logic
├── key.json           # Stores the OpenAI API key (ensure this is never exposed)
├── requirements.txt   # Python dependencies
├── store/             # Directory where FAISS index is stored (per PDF)
│    ├── terms/
│    ├── privacy/
│    └── ...
├── docs/              # Directory where uploaded PDFs are stored
```

---

## 4. **Installation Steps**

1. **Clone the repository**:
   ```bash
   git clone <your_repo_url>
   cd <your_repo_folder>
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Mac/Linux
   venv\Scripts\activate  # For Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your OpenAI API Key**:
   - Create a `key.json` file with the following structure:
     ```json
     {
       "OPENAI_API_KEY": "your_openai_api_key"
     }
     ```

5. **Run the app**:
   ```bash
   streamlit run main.py
   ```

---

## 5. **How It Works**

### a) **PDF Upload and Processing**
1. **User uploads a PDF file** through the Streamlit interface.
2. The file is saved in the `/docs` directory.
3. The system uses **PyPDF2** to extract text and **LangChain's RecursiveCharacterTextSplitter** to split the text into smaller, meaningful chunks.
4. These chunks are then embedded using **OpenAIEmbeddings** to create vectors, which are stored in **FAISS** for fast search.

### b) **FAISS Vector Store**
- **FAISS** is a highly efficient library for **vector similarity search**.
- Each PDF has its own FAISS index saved in a folder inside `/store/`.
- If the PDF content is unchanged, it reuses the existing FAISS index.
- If the content changes (based on file hash comparison), it rebuilds the vector store.

### c) **Question Answering**
- **ConversationalRetrievalChain** from LangChain uses the FAISS index to retrieve the most relevant parts of the document.
- **OpenAI's GPT model** is then used to answer the question based on the retrieved information.

### d) **File Change Detection**
- **MD5 hashing** is used to detect changes in PDF content.
- If the uploaded PDF is the same (same name, same content), the system skips reprocessing and uses the existing FAISS index.
- If the content is updated (even with the same name), a new FAISS index is created and saved.

---

## 6. **Code Breakdown**

### 1. **`main.py`** - Streamlit Application
- **Functionality**: 
  - Displays the interface.
  - Handles file upload.
  - Passes the uploaded file to `pdf_loader.py` for processing.
  - Runs Q&A based on the processed PDF content using `qa_engine.py`.
  
```python
import os
import json
import streamlit as st
from pdf_loader import load_and_split_pdf
from embedder import create_or_load_vector_store
from qa_engine import create_qa_chain

# Load OpenAI API Key from key.json
parent_dir = os.path.dirname(os.path.abspath(__file__))
key_path = os.path.join(parent_dir, 'key.json')

with open(key_path) as f:
    key_data = json.load(f)

os.environ["OPENAI_API_KEY"] = key_data["OPENAI_API_KEY"]

# Create folders if not exist
os.makedirs("docs", exist_ok=True)
os.makedirs("store", exist_ok=True)

def main():
    st.title("📄 AI PDF Q&A Bot")
    st.write("Upload a PDF and ask questions about it!")

    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

    if uploaded_file:
        pdf_path = os.path.join("docs", uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Create a unique store path per PDF
        pdf_name = os.path.splitext(uploaded_file.name)[0]
        store_path = os.path.join("store", pdf_name)

        docs = load_and_split_pdf(pdf_path)
        vector_store = create_or_load_vector_store(docs, store_path, pdf_path)

        qa_chain = create_qa_chain(vector_store)

        st.success(f"PDF '{uploaded_file.name}' uploaded and processed successfully!")

        query = st.text_input("Ask your question:")

        if query:
            response = qa_chain.run(query)
            st.write("### Answer:")
            st.write(response)

if __name__ == "__main__":
    main()
```

### 2. **`pdf_loader.py`** - PDF Loading and Chunking
- **Functionality**: Extracts text from PDFs and splits them into chunks using LangChain's `RecursiveCharacterTextSplitter`.

```python
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_and_split_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    docs = splitter.split_documents(documents)
    return docs
```

### 3. **`embedder.py`** - FAISS Vector Store Management
- **Functionality**: Creates and loads FAISS index, comparing the file hash to detect content changes.

```python
import os
import hashlib
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

def get_file_hash(pdf_path):
    """Get the hash of the file to check if it changed."""
    hasher = hashlib.md5()
    with open(pdf_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def create_or_load_vector_store(docs, folder_path, pdf_path):
    if os.path.exists(folder_path):
        saved_hash = None
        try:
            with open(os.path.join(folder_path, "file_hash.txt"), "r") as f:
                saved_hash = f.read().strip()
        except FileNotFoundError:
            pass

        current_hash = get_file_hash(pdf_path)

        if saved_hash != current_hash:
            embeddings = OpenAIEmbeddings()
            vector_store = FAISS.from_documents(docs, embeddings)
            vector_store.save_local(folder_path)
            with open(os.path.join(folder_path, "file_hash.txt"), "w") as f:
                f.write(current_hash)
        else:
            vector_store = FAISS.load_local(folder_path, OpenAIEmbeddings())
    else:
        embeddings = OpenAIEmbeddings()
        vector_store = FAISS.from_documents(docs, embeddings)
        vector_store.save_local(folder_path)
        with open(os.path.join(folder_path, "file_hash.txt"), "w") as f:
            f.write(get_file_hash(pdf_path))

    return vector_store
```

### 4. **`qa_engine.py`** - Q&A Chain
- **Functionality**: Creates a question-answering chain using the FAISS index and OpenAI's model for answering questions.

```python
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory

def create_qa_chain(vector_store):
    llm = OpenAI(temperature=0)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    qa = ConversationalRetrievalChain.from_llm(
        llm,
        retriever=vector_store.as_retriever(),
        memory=memory
    )
    return qa
```

---

## 7. **Enhancements and Future Work**

- **Add support for multiple PDFs**: Allow users to upload multiple PDFs and search across them.
- **Persistent memory**: Keep track of the conversation even if the user reloads the page.
- **Export answers**: Option to export the Q&A session as a PDF or text file.
- **Improve UI**: Enhance Streamlit UI with richer design and UX improvements.

---

## 8. **Conclusion**

This **AI PDF Q&A Bot** leverages powerful AI tools (LangChain, OpenAI, FAISS) to provide users with a seamless way to interact with the content of any PDF document. By processing PDF content into vector embeddings and using semantic search, users can ask meaningful questions and get relevant answers from the document.

---

If you need further adjustments or clarifications, feel free to ask! 📚🚀