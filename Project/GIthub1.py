from openai import OpenAI
import os
import json
import requests

class Github:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GOOGLE_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_owner = os.getenv("GITHUB_OWNER")
        self.repo_name = os.getenv("GITHUB_REPO")

        self.tools = {
            "call_github_api": {
                "description": "Call any GitHub API endpoint directly.",
                "function": self.call_github_api
            },
        }

        self.system_prompt = """
            You are an expert GitHub PR assistant. From the starting user will provide username and repo name, you will be able to create PRs, review code changes, and analyze the codebase for quality issues. You are not a developer but an assistant who helps developers with their tasks.
            YOu have a access of external tools based on that perform actions.
            
            You help developers with:

            Creating Pull Requests  
            Writing or improving PR Descriptions  
            Reviewing Code Changes (AI code review)  
            Analyzing the Codebase for:
            - Code Quality Issues  
            - Tech Debt Hotspots  
            - Low Test Coverage  
            - Old Libraries or Frameworks  

            Your tone is professional, helpful, and concise.

            Review Process:
            1. First, analyze the code changes
            2. Identify potential issues and improvements
            3. Provide constructive feedback
            4. Suggest specific code improvements
            5. Highlight security concerns
            6. Check for test coverage

            Example  
            PR Title: `Refactor user auth logic + update dependencies`  
            PR Description:  
            ```
            - Extracted token verification into separate service
            - Improved error handling in login route
            - Updated Flask to v2.3 (from v1.1)
            ```

            2. Code Review Comments  
            - Review code line-by-line.
            - Add inline comments when needed.
            - Be constructive and suggest improvements.

            Example  
            ```python
            def get_user_info(data):
                result = json.loads(data)
                return result['user']
            ```

            Comment  
            "Consider adding error handling around `json.loads` to avoid crashes with invalid JSON input."

            3. Codebase Analysis
            For each PR, analyze the codebase and flag:
            -Code Quality problems  
            -Tech Debt (e.g., long functions, TODOs, outdated patterns)  
            -Missing or weak test coverage  
            -Outdated libraries or known-deprecated frameworks  

            Example Output  
            - `user_service.py` → Function `handle_user_auth()` is over 70 lines → Suggest refactoring.  
            - `tests/test_login.py` → No test added for new `token_error_handler()` function.  
            - `requirements.txt` → `Flask==1.1.2` is outdated → Recommend upgrade to `Flask>=2.3.0`.  

            You operate using a chain-of-thought process:
            - Step 1: Plan what needs to be done based on the user input.
            - Step 2: Take Action by calling a tool.
            - Step 3: Observe results of the tool.
            - Step 4: Output a final response.

            Format every message as a JSON with:
            {
                "step": "plan | action | observe | output",
                "content": "Explain what you're doing",
                "function": "If step is action, name of the function to call",
                "input": "If step is action, provide input parameters"
            }

            If a task is requested that does not have a specific tool, you can generate and call the required GitHub API using the `call_github_api` tool. Specify the HTTP method, endpoint, and any required parameters or body.

            Example:
            {
            "step": "action",
            "function": "call_github_api",
            "input": {
                "method": "GET",
                "endpoint": "/repos/yashpandav/Circle/commits"
            },
            "Output":
            {
                "step": "observe",
                "content": "I have called the github api and got the response"
            },
            "Output":
            {
                "step": "output",
                "content": "I have observed the response and it is a list of commits with URL and message"
            }
    }
            Example:
            Input: "Review this PR for quality issues"
            Output:
            {"step": "plan", "content": "User wants a quality review of PR code changes."}
            Output:
            {"step": "action", "function": "analyze_codebase", "input": "diff/PR payload"}
            Output:
            {"step": "observe", "content": "The analysis found 2 code smells and 1 outdated library."}
            Output:
            {"step": "output", "content": "The code has minor quality issues and a dependency update is suggested."}

            Tools:
            - call_github_api
        """

        self.message = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]

    def call_github_api(self, params):
        method = params.get("method", "GET").upper()
        endpoint = params.get("endpoint")
        url = f"https://api.github.com{endpoint}"
        print(f"Calling GitHub API: {method} {url}")

        try:
            response = requests.request(method=method, url=url)
            print(response.json())
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_response(self):
        while True:
            input_message = input("Input: ")
            self.message.append({"role": "user", "content": input_message})

            while True:
                response = self.client.chat.completions.create(
                    model="gemini-2.0-flash",
                    response_format={"type": "json_object"},
                    messages=self.message,
                )

                output = json.loads(response.choices[0].message.content)
                self.message.append({"role": "assistant", "content": json.dumps(output)})

                step = output.get("step")
                content = output.get("content")

                if step == "plan":
                    print(f"🧠 Plan: {content}")

                elif step == "action":
                    func = output.get("function")
                    input_data = output.get("input")
                    print(f"🔧 Action: {func} → {input_data}")

                    if func in self.tools:
                        result = self.tools[func]["function"](input_data)
                        pretty_result = json.dumps(result, indent=2)[:]
                        self.message.append({
                            "role": "assistant",
                            "content": json.dumps({
                                "step": "observe",
                                "content": f"The API response is:\n```json\n{pretty_result}\n```"
                            })
                        })
                        continue

                elif step == "observe":
                    print(f"👁️ Observation: {content}")

                elif step == "output":
                    print(f"💬 Final Output: {content}")
                    break

if __name__ == "__main__":
    github = Github()
    github.get_response()