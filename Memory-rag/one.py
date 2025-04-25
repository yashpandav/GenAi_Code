from mem0 import Memory
from openai import OpenAI
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# qdrant = QdrantClient(host="localhost", port=6333)

# qdrant.recreate_collection(
#     collection_name="test",
#     vectors_config=VectorParams(size=768, distance=Distance.COSINE),
# )

load_dotenv()

QUADRANT_HOST = "localhost"

NEO4J_URL="bolt://localhost:7687"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="HW6sA8eTZrRaX4blwY-KWgt-vPhocUSZqIz2IfNC6EM"

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "gemini",
        "config": {
            "model": "models/text-embedding-004",
        }
    },
    "llm": {
        "provider": "gemini",
        "config": {
            "model": "gemini-1.5-flash-latest",
            "temperature": 0.2,
            "max_tokens": 2000,
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "test",
            "host": "localhost",
            "port": 6333,
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {"url": NEO4J_URL, "username": NEO4J_USERNAME, "password": NEO4J_PASSWORD},
    },
}

memory = Memory.from_config(config)

Client = OpenAI(
            api_key=os.getenv("GOOGLE_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def chat(message):
    
    mem_result = memory.search(query=message, user_id="user_1")
    print(mem_result)


    memories = "\n".join([m["memory"] for m in mem_result.get("results")])


    SYSTEM_PROMPT = f"""
        You are a Memory-Aware Fact Extraction Agent, an advanced AI designed to
        systematically analyze input content, extract structured knowledge, and maintain an
        optimized memory store. Your primary function is information distillation
        and knowledge preservation with contextual awareness.
        Tone: Professional analytical, precision-focused, with clear uncertainty signaling
        
        Memory and Score:
        {memories}
    """

    messages = [
        { "role": "system", "content": SYSTEM_PROMPT },
        { "role": "user", "content": message }
    ]

    reponse = Client.chat.completions.create(
        model="gemini-1.5-flash-latest",
        messages=messages
    )


    messages.append(
        { "role": "assistant", "content": reponse.choices[0].message.content }
    )

    memory.add(messages, user_id="user_1")

    return reponse.choices[0].message.content

while True:
    message = input(">> ")
    print("BOT: ", chat(message=message))
    