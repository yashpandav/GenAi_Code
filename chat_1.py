from google import genai
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()


client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

response = client.chat.completions.create(
    model="gemini-2.0-flash",
    n=3,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Explain to me how AI work in very brief"
        }
    ]
)


for i, choice in enumerate(response.choices):
    print(f"Option {i+1}: {choice.message.content}")