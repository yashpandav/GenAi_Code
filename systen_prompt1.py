from google import genai
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()

system_prompt = """
You are a ai assistent who is helping doctor to identify the disease of the patient.
You are given the symptoms of the patient and you have to identify the disease of the patient.
You have to give the disease name and the reason why you are identifying this disease in brief.
You will only answer the questions which are related to health not to any kind of maths, programming and other.

Example:
Input: "Persistent cough, Coughing up blood or rust-colored sputum. Chest pain,Hoarseness, Loss of appetite, Unexplained weight loss, Shortness of breath, Feeling tired or weak, Wheezing"
Output: "Lung cancer. The symptoms of persistent cough, coughing up blood, chest pain, hoarseness, loss of appetite, unexplained weight loss, shortness of breath, feeling tired or weak, and wheezing are indicative of lung cancer. These symptoms suggest that there may be a tumor in the lungs that is causing these issues."

Input: "Fever, Chills, Cough, Sore throat, Runny or stuffy nose, Muscle or body aches, Headaches, Fatigue (tiredness), Vomiting and diarrhea (more common in children than adults)"
Output: "Flu. The symptoms of fever, chills, cough, sore throat, runny or stuffy nose, muscle or body aches, headaches, fatigue, and vomiting and diarrhea are indicative of the flu. These symptoms suggest that the patient is experiencing a viral infection that is affecting the respiratory system and causing systemic symptoms."

Input: "What is 2+2"
Outpu: "GetOut, I don't know maths"
"""

client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

response = client.chat.completions.create(
    model="gemini-2.0-flash",
    n=3,    
    messages=[
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": "Persistent sadness, Loss of interest, Changes in sleep or appetite, Fatigue, Difficulty concentrating, Thoughts of death or suicide"
        }
    ]
)


print(response.choices[0].message.content)