from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI
from langchain.agents.agent_toolkits import create_retriever_tool, create_conversational_retrieval_agent
from langchain_openai.chat_models import ChatOpenAI
import os
import json

# Load OpenAI API Key
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
key_path = os.path.join(parent_dir, 'key.json')

with open(key_path) as f:
    key_data = json.load(f)

os.environ["OPENAI_API_KEY"] = key_data["openai_api_key"]

# Load and split PDF
pdf = PyPDFLoader("docs/Atomic habits.pdf")
pdfpages = pdf.load_and_split()

# Split into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=0)
split_text = text_splitter.split_documents(pdfpages)

# Create vectorstore
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(split_text, embeddings)
vectorstore_retriever = vectorstore.as_retriever()

# Create retriever tool
tool = create_retriever_tool(
    vectorstore_retriever,
    "Atomic_Habits_Chapter_Search",
    "Retrieve detailed information about the chapters of the book Atomic Habits by James Clear."
)

tools = [tool]

# Create LLM and agent
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
myagent = create_conversational_retrieval_agent(
    llm=llm,
    tools=tools,
    verbose=False
)

# Create context and prompt
context = "The user is conducting research on Atomic Habits by James Clear and is seeking detailed information on the chapters of the book."

question = "What are the three laws explained in the book Atomic Habits by James Clear?"

prompt = f"""
You are an assistant helping a student study the book 'Atomic Habits' by James Clear.
Answer ONLY based on the provided PDF content. 
Do NOT make up information. 
Use the exact wording or close wording from the document if possible.
Context = {context}
Question = {question}
"""

# Invoke the agent
result = myagent.invoke({"input": prompt})

print(result)
