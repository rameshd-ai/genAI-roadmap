from langchain_community.document_loaders import PyPDFLoader

# Change the PDF file
pdf = PyPDFLoader("docs/business_info.pdf")  # <--- Your business info PDF

pdfpages = pdf.load_and_split()

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import os
from langchain_openai import OpenAI
import json

# Load API key
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
key_path = os.path.join(parent_dir, 'key.json')

with open(key_path) as f:
    key_data = json.load(f)

os.environ["OPENAI_API_KEY"] = key_data["openai_api_key"]

# Load the document
mybooks = pdf.load()

# Chunk the document
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=0)
split_text = text_splitter.split_documents(mybooks)

# Create vectorstore
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(split_text, embeddings)

vectorstore_retriever = vectorstore.as_retriever()

from langchain.agents.agent_toolkits import create_retriever_tool

tool = create_retriever_tool(
    vectorstore_retriever,
    "Business_Info_Company_Search",
    "Retrieve detailed information about companies listed inside the Business Info document."
)

tools = [tool]

from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain_openai.chat_models import ChatOpenAI

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

myagent = create_conversational_retrieval_agent(
    llm=llm,
    tools=tools,
    verbose=False
)

context = "The user is asking about companies mentioned inside the Business Info PDF."
question = "What is Oravil?"

prompt = f"""You need to answer the question exactly based on the document content.
If information is NOT found, say: 'Information not found in document.'
Context = {context} 
Question = {question}
"""

# Final invoke
result = myagent.invoke({"input": prompt})

print(result['output'])  # Output the answer
