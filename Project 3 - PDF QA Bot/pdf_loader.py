from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pytesseract
from pdf2image import convert_from_path
import os

def load_and_split_pdf(pdf_path):
    """Load PDF and split it into chunks, using OCR if no extractable text is found."""
    
    # Attempt to extract text using PyPDFLoader
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # If no text was extracted, try OCR on the PDF
    if not documents:
        print(f"No extractable text found in {pdf_path}. Attempting OCR.")
        
        # Convert PDF pages to images using pdf2image
        images = convert_from_path(pdf_path)
        
        # Extract text from images using pytesseract
        ocr_text = ""
        for image in images:
            ocr_text += pytesseract.image_to_string(image)
        
        # If OCR text is still empty, raise an error
        if not ocr_text.strip():
            raise ValueError(f"PDF contains no extractable text and OCR failed: {pdf_path}")
        
        # Create a document with the OCR text
        documents = [{"page_content": ocr_text}]
    
    # Split the text into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    
    docs = splitter.split_documents(documents)
    
    if not docs:
        raise ValueError(f"No chunks were created from the PDF: {pdf_path}")
    
    return docs
