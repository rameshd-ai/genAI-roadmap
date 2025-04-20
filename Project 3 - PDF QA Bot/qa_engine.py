from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory

def create_qa_chain(vector_store):
    """Create a Q&A chain using LangChain's conversational retriever"""
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
