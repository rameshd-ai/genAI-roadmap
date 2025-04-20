import os
import hashlib
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

def get_file_hash(pdf_path):
    """Get MD5 hash of the file to detect changes."""
    hasher = hashlib.md5()
    with open(pdf_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def create_or_load_vector_store(docs, folder_path, pdf_path):
    """Create or load FAISS vector store for a given PDF."""

    if not docs or len(docs) == 0:
        raise ValueError("No documents found after PDF split. Please check the PDF content.")

    # Ensure store folder exists
    os.makedirs(folder_path, exist_ok=True)

    # Check if vectorstore already exists
    if os.path.exists(folder_path):
        saved_hash = None
        try:
            with open(os.path.join(folder_path, "file_hash.txt"), "r") as f:
                saved_hash = f.read().strip()
        except FileNotFoundError:
            pass

        current_hash = get_file_hash(pdf_path)

        if saved_hash != current_hash:
            # If hash mismatch → recreate vector store
            embeddings = OpenAIEmbeddings()
            vector_store = FAISS.from_documents(docs, embeddings)
            vector_store.save_local(folder_path)

            with open(os.path.join(folder_path, "file_hash.txt"), "w") as f:
                f.write(current_hash)
        else:
            # If hash same → load existing vector store
            vector_store = FAISS.load_local(
                folder_path,
                OpenAIEmbeddings(),
                allow_dangerous_deserialization=True
            )
    else:
        # If no folder exists → create new vector store
        embeddings = OpenAIEmbeddings()
        vector_store = FAISS.from_documents(docs, embeddings)
        vector_store.save_local(folder_path)

        with open(os.path.join(folder_path, "file_hash.txt"), "w") as f:
            f.write(get_file_hash(pdf_path))

    return vector_store
