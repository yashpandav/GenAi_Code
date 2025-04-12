import os
import json
import subprocess
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AutoAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GOOGLE_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        self.project_context = {
            "current_directory": os.getcwd(),
            "project_structure": {},
            "file_contents": {}
        }

        self.system_prompt = """
You are CodeCraft, an expert AI coding assistant specialized in full-stack development. 
You work in a start→plan→action→observe→output cycle to help users build complete projects through the terminal.

You have deep expertise in:
- Frontend: React, Vue, Angular, HTML/CSS, JavaScript/TypeScript
- Backend: Node.js, Python (Django, Flask), Java (Spring), Ruby on Rails
- Database: SQL, MongoDB, Firebase
- DevOps: Docker, CI/CD, AWS, deployment processes

INSTRUCTIONS:
1. Maintain a model of the project structure and files
2. Suggest appropriate architecture and best practices
3. Generate complete, working code when needed
4. Execute terminal commands to install dependencies, create files, or run builds
5. Modify existing code in context when adding features
6. Provide clear explanations for your decisions

Always follow this workflow:
1. PLAN: Think about the request and determine the best approach
2. ACTION: Select and use an appropriate tool with exact parameters
3. OBSERVE: Review the result of your action
4. OUTPUT: Explain what you did, what happened, and what to do next

Rules:
- Follow the strict Output JSON Format
- Perform one step at a time and wait for next input
- Analyze existing code before modifying it
- Ensure commands are appropriate for the current OS (Windows assumed)
- When asked to build something, create proper file structures and all necessary files

Output JSON Format:
{
    "step" : "string (plan|action|observe|output)",
    "content" : "string (explanation)",
    "function" : "string (only when step is action)",
    "input" : "any (parameters for function call)",
    "code" : "string (code to be written)"
}

Available Tools:
- command_exec: Executes a terminal command and returns the result
- read_file: Reads the content of a specified file to understand context
- write_file: Creates or updates a file with specified content
- scan_directory: Lists files in a directory to understand project structure
- analyze_code: Analyzes existing code to understand its structure and purpose
"""

        self.available_tools = {
            "command_exec": {
                "description": "Execute a terminal command",
                "function": self.command_exec
            },
            "read_file": {
                "description": "Read the content of a file",
                "function": self.read_file
            },
            "write_file": {
                "description": "Create or update a file with content",
                "function": self.write_file
            },
            "scan_directory": {
                "description": "List files in a directory",
                "function": self.scan_directory
            },
            "analyze_code": {
                "description": "Analyze existing code structure",
                "function": self.analyze_code
            }
        }

        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    def command_exec(self, command):
        print("🔑 ", command)
        return subprocess.run(command)

    def read_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                print(f"📄 Read file: {file_path}")
                self.project_context["file_contents"][file_path] = content
                return content
        except FileNotFoundError:
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def write_file(self, params):
        file_path = params.get("path")
        content = params.get("content")
        print(f"📝 Writing to file: {file_path}"
              f" with content: {content}")
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as file:
                file.write(content)
                self.project_context["file_contents"][file_path] = content
                return f"File {file_path} written successfully."
        except Exception as e:
            return f"Error writing file: {str(e)}"

    def scan_directory(self, directory):
        try:
            files = os.listdir(directory)
            print(f"📂 Scanned directory: {directory} with files: {files}")
            self.project_context["project_structure"][directory] = files
            return files
        except Exception as e:
            return f"Error scanning directory: {str(e)}"

    def analyze_code(self, file_path):
        try:
            print(f"🔍 Analyzing code in file: {file_path}")
            with open(file_path, 'r') as file:
                content = file.read()
                self.project_context["file_contents"][file_path] = content
                # Placeholder for actual analysis logic
                return f"Analyzed code in {file_path}."
        except Exception as e:
            return f"Error analyzing code: {str(e)}"

    def run(self):
        while True:
            query = input("> ")
            self.messages.append({"role": "user", "content": query})

            while True:
                response = self.client.chat.completions.create(
                    model="gemini-2.0-flash",
                    response_format={"type": "json_object"},
                    messages=self.messages,
                )

                parsed_output = json.loads(response.choices[0].message.content)
                self.messages.append({
                    "role": "assistant",
                    "content": json.dumps(parsed_output)
                })

                step = parsed_output.get("step")

                if step == 'plan':
                    print(f"🧠: {parsed_output.get('content')}")

                if step == 'action':
                    print(f"🔨 Executing: {parsed_output.get('function')}")
                    function = parsed_output.get("function")
                    user_input = parsed_output.get("input")

                    if function in self.available_tools:
                        tool = self.available_tools.get(function)
                        result = tool.get("function")(user_input)
                        self.messages.append({
                            "role": "assistant",
                            "content": json.dumps({
                                "step": "observe",
                                "content": result,
                            })
                        })
                        continue

                    

                if step == "output":
                    print(f"💬: {parsed_output.get('content')}")
                    break


if __name__ == "__main__":
    agent = AutoAgent()
    agent.run()
