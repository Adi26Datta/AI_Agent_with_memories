import os
from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph 
from langchain_openai import ChatOpenAI

load_dotenv()
llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)

def load_neo4j_graph() -> Neo4jGraph:
    # Load from environment
    load_dotenv()
    # Initialize Neo4j graph object
    graph = Neo4jGraph(
        url=os.getenv('NEO4J_URI'),
        username=os.getenv('NEO4J_USERNAME'),
        password=os.getenv('NEO4J_PASSWORD'),
        database=os.getenv('NEO4J_DATABASE') or 'neo4j'
    )
    return graph
