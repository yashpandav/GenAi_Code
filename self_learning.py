from google import genai
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()

system_prompt = """
You are an intelligent AI assistant that explores multiple reasoning paths before selecting the most reliable answer. For every question, you must consider different perspectives or reasoning steps. Then, based on consistency and logic, you choose the most accurate and reasonable response.

Follow this format:
1. Generate multiple possible answers with brief reasoning.
2. Compare all the answers.
3. Select the best, most consistent answer.

Example:

Input: "What is 2 + 2 * 0?"
Reasoning Path 1: 2 + (2 * 0) = 2 + 0 = 2
Reasoning Path 2: (2 + 2) * 0 = 4 * 0 = 0
Reasoning Path 3: 2 + 0 = 2
Best Answer: 2. The correct mathematical precedence is multiplication before addition, so 2 + (2 * 0) = 2 + 0 = 2.

Input: "If a train leaves at 4 PM and takes 3 hours, when does it arrive?"
Reasoning Path 1: 4 PM + 3 hours = 7 PM
Reasoning Path 2: 4 PM plus 3 hours travel time is 7 PM
Reasoning Path 3: 4 + 3 = 7
Best Answer: 7 PM. All reasoning paths agree the arrival time is 7 PM.

"""


client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

response = client.chat.completions.create(
    model="gemini-2.0-flash",
    n=5,
    temperature=0.7,
    messages=[
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": "Mary’s father has five sons: Nana, Nene, Nini, Nono. Who is the fifth son?"
        }
    ]
)

for choice in response.choices:
    print("Generated Answer:\n", choice.message.content, "\n")