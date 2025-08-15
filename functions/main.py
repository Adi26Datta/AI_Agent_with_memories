from pydantic import BaseModel, Field
from langchain_core.tools import tool
from functions.config import llm
from langgraph.prebuilt.chat_agent_executor import create_react_agent
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Neo4jVector
from dotenv import load_dotenv
import os
from functions.Memory.memory import short_term_memory_store, load_and_save_long_term


# Define output model
class FinalOutput(BaseModel):
    """Respond to the user in this format."""
    print("FinalOutput model initialized.")
    response: str = Field(description="First check the human message, if the query needed tool message, use it, otherwise use AI message to respond")

load_dotenv()

# Function to query the vector store
def query_vector_rag(question: str, top_k: int = 3):
    print(f"Querying vector store with question: {question}")
    vector_store = Neo4jVector.from_existing_graph(
        embedding=OpenAIEmbeddings(),
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        index_name='Chunk',
        node_label='Chunk',
        text_node_properties=['text'],
        embedding_node_property='textEmbeddingOpenAI',
    )
    docs_and_scores = vector_store.similarity_search_with_score(
        question, 
        k=3
    )
    print(f"Found {len(docs_and_scores)} documents with scores.")
    return docs_and_scores

# Tool wrapper
@tool
def get_vector_response(question, top_k=5):
    """Use this to get vector response from database."""
    print(f"Paasing through tool")
    return query_vector_rag(question=question)

# List of tools
tools_list = [get_vector_response]

# Create the agent
AgentToolCall = create_react_agent(
    llm,
    tools=tools_list,
    response_format=FinalOutput,
    checkpointer=short_term_memory_store,
    state_modifier=load_and_save_long_term,
)
