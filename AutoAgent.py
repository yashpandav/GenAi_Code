from google import genai
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from requests import request
load_dotenv()

def get_weather(city: str):
    print("🔨 Tool Called: get_weather", city)
    
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = request("GET", url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    return "Something went wrong"

def command_exec(command: str):
    print("🔑 ", command)
    result = os.system(command)
    return result


availabe_tools = {
    "get_weather_data": {
        "description": "Take a input a city name and returns the weather data of the city.",
        "function": get_weather
    },
    "command_exec": {
        "description": "Take a input a command, executes the command and returns the result of the command.",
        "function": command_exec
    }
}

system_prompt = """
    You are an helpfull AI Assistant who is specialized in resolving user query.
    You work on start, plan, action, observe mode.
    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.
    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query
    - Command should be able to run on windows machine
    
    Output JSON Format:
        {{
            "step" : "string",
            "content" : "string",
            "function" : "name of function if step is action",
            "input" : "input parameter of function",
        }}

    Available Tools:
    - get_weather_data : Take a input a city name and returns the weather data of the city. 
    - command_exec : Take a input a command, execute command and returns the result of the command.

    Example:
    Input : What is the current weather in New York?
    Output: {{"step" : "plan", "content" : "user is asking for weather data"}}
    Output: {{"step" : "plan", "content" : "first i should check is there any weather data available in my memory"}}
    Output: {{"step" : "plan", "content" : "for weather data i should call get_weather_data tool"}}
    Output: {{"step" : "action", "function" : "get_weather_data" "input" : "New York"}}
    Output: {{"step" : "observe", "content" : "weather data is available in my memory"}}
    Output: {{"step" : "output" , "content" : "The current weather in New York is 25 degree celsius"}}

    Example: 
    Input : list the directory
    Output: {{"step" : "plan", "content" : "user is asking for directory listing"}}
    Output: {{"step" : "plan", "content" : "for directory listing i should call command_exec tool"}}
    Output: {{"step" : "action", "function" : "command_exec" "input" : "dir"}}
    Output: {{"step" : "output" , "content" : "The current directory listing is: file1.txt, file2.txt"}}

"""

client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

message = [
    {
            "role": "system", "content" : system_prompt,
    },
]

while True:
    query = input("> ")
    message.append({ "role": "user", "content": query })

    while True:
        response  = client.chat.completions.create(
            model="gemini-2.0-flash",
            response_format={"type": "json_object"},
            messages=message,
        )

        parsed_ouput = json.loads(response.choices[0].message.content)

        message.append({
            "role" : "assistant",
            "content" : json.dumps(parsed_ouput)
        })

        if(parsed_ouput.get("step") == 'plan') :
            print(f"🧠: {parsed_ouput.get("content")}")

        if(parsed_ouput.get("step") == 'action') :
            print(f"🔨: {parsed_ouput.get("function")}")
            function = parsed_ouput.get("function")
            user_input = parsed_ouput.get("input") 

            if function in availabe_tools:
                tool = availabe_tools.get(function)
                result = tool.get("function")(user_input)
                message.append({
                    "role" : "assistant",
                    "content" : json.dumps({
                        "step" : "observe",
                        "content" : result,
                    })
                })
                continue
        
        if(parsed_ouput.get("step") == "output") :
            print(f"💬: {parsed_ouput.get("content")}")
            break