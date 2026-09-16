import os
from typing import TypedDict
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, START, END

# Load Environment Variables
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyBIba32PjVOzlE67GxIDCUF9ApgBrFpVWo")

# Initialize LLM and Embeddings
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=api_key
)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=api_key
)

# Initialize Chroma Vector Store
vectorstore = Chroma(
    collection_name="chroma_db",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3}
)

# LangGraph State Schema
class State(TypedDict):
    question: str
    documents: list
    answer: str

# Retrieve Node
def retrieve_node(state: State):
    question = state["question"]
    documents = retriever.invoke(question)
    return {"documents": documents}

# Generate Node
def generate_node(state: State):
    question = state["question"]
    documents = state["documents"]

    context = "\n\n".join(doc.page_content for doc in documents)

    prompt = f"""
    Answer the question using only the context below.

    Context:
    {context}

    Question:
    {question}

    If the answer is not present in the context,
    say "I don't know based on the provided document."
    """

    response = llm.invoke(prompt)
    return {"answer": response.content}

# Build LangGraph Pipeline
graph = StateGraph(State)
graph.add_node("retrieve", retrieve_node)
graph.add_node("generate", generate_node)
graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)

rag_app = graph.compile()

# Primary function exposed to API
def ask_rag(question: str) -> str:
    try:
        result = rag_app.invoke({
            "question": question,
            "documents": [],
            "answer": ""
        })
        return result.get("answer", "No answer generated.")
    except Exception as e:
        print(f"Error in ask_rag: {e}")
        return f"Error processing request: {str(e)}"