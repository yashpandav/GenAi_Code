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
-When using write_file:
    - The 'input' MUST be a JSON object with:
    - "path": Full file path (e.g., "src/math.js")
    - "content": File contents as string
- When reading files:
  - Always specify full paths
  - Handle encoding automatically
  - Display contents in readable format
- Command to be executed must be a string, if it is dictionary than find the command string from the dictionary.
- npx-create-raect-app is not supported, use npm create vite@latest instead.
Output JSON Format 

WORKFLOW EXAMPLES:

1. DIRECTORY SCANNING:
Output: {"step": "plan", "content": "User wants directory listing of current folder"}
Output: {"step": "action", "function": "scan_directory", "input": "."}
Output: {"step": "observe", "content": ["file1.txt", "src/", "package.json"]}
Output: {"step": "output", "content": "Current directory contains: file1.txt, src/, package.json"}

2. FILE READING:
Output: {"step": "plan", "content": "User wants to read package.json contents"}
Output: {"step": "action", "function": "read_file", "input": "package.json"}
Output: {"step": "observe", "content": "{\\"name\\": \\"my-app\\", ...}"}
Output: {"step": "output", "content": "package.json contains project configuration..."}

3. FILE WRITING:
Output: {"step": "plan", "content": "Need to create math.js with add function"}
Output: {"step": "action", "function": "write_file", "input": {"path": "math.js", "content": "function add(a,b){return a+b}"}}
Output: {"step": "observe", "content": "File math.js written successfully"}
Output: {"step": "output", "content": "Created math.js with add function"}

4. COMMAND EXECUTION:
Output: {"step": "plan", "content": "User wants to install dependencies"}
Output: {"step": "action", "function": "command_exec", "input": "npm install"}
Output: {"step": "observe", "content": "added 125 packages"}
Output: {"step": "output", "content": "Dependencies installed successfully"}

5. CODE ANALYSIS:
Output: {"step": "plan", "content": "Need to analyze app.js structure"}
Output: {"step": "action", "function": "analyze_code", "input": "src/app.js"}
Output: {"step": "observe", "content": "File contains React component with 3 hooks"}
Output: {"step": "output", "content": "app.js contains main App component with useState, useEffect hooks"}

RULES:
1. STRICT JSON FORMAT - Every response must be valid JSON matching examples
2. SINGLE STEP - Only perform one action per response
3. VALIDATION - Verify paths/inputs before execution
4. CONTEXT - Maintain project structure awareness
5. EXPLANATION - Always explain actions in output step

TOOLS:
- scan_directory(path): List files in directory
- read_file(path): Read file contents (auto-handles encoding)
- write_file({path,content}): Create/update file
- command_exec(cmd): Run terminal command
- analyze_code(path): Examine code structure

ERROR HANDLING EXAMPLES:
Output: {"step": "output", "content": "Error: Invalid path provided for read_file"}
Output: {"step": "output", "content": "Error: write_file requires {path:, content:} format"}
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
        return os.system(command)
    def read_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                print(f"📄 Read file: {file_path}")
                print("📜 Content:")
                print("-" * 40)
                print(content)
                print("-" * 40)
                self.project_context["file_contents"][file_path] = content
                return content
        except UnicodeDecodeError:
            try:
                # Try with different encoding if utf-8 fails
                with open(file_path, 'r', encoding='latin-1') as file:
                    content = file.read()
                    print(f"📄 Read file (latin-1 encoding): {file_path}")
                    print("📜 Content:")
                    print("-" * 40)
                    print(content)
                    print("-" * 40)
                    self.project_context["file_contents"][file_path] = content
                    return content
            except Exception as e:
                return f"Error reading file with fallback encoding: {str(e)}"
        except FileNotFoundError:
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    def write_file(self, params):
        if not isinstance(params, dict):
            return "Error: Parameters must be a dictionary with 'path' and 'content'"
        
        file_path = params.get("path")
        content = params.get("content")
        
        if not file_path:
            return "Error: Missing 'path' parameter for file creation"
        if not content:
            return "Error: Missing 'content' parameter for file creation"

        print(f"📝 Writing to file: {file_path}")
        print("🖨️ Content:")
        print("-" * 40)
        print(content)
        print("-" * 40)

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
                        if function == "write_file" and (not isinstance(user_input, dict) or 'path' not in user_input):
                                print("❌ Invalid write_file parameters")
                                self.messages.append({
                                    "role": "system",
                                    "content": "ERROR: write_file requires {path: '...', content: '...'} format"
                                })
                                continue
                        tool = self.available_tools.get(function)
                        if function == "command_exec":
                            print("🔑 ", user_input)
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
