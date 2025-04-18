# TeaCoder AI Coding Assistant

A terminal-based AI Agent focused on coding and full-stack project development. This agent functions entirely through the terminal and performs a wide range of development tasks.

## Features

- Terminal-based interface (no GUI)
- Specialized in creating full-stack projects
- Can generate folder and file structures
- Writes code into appropriate files (frontend and backend)
- Runs commands like `npm install`, `pip install`, etc.
- Supports follow-up prompts for iterative development
- Understands context from existing project files
- Non-interactive command handling for npm/npx create commands

## Requirements

- Python 3.6+
- OpenAI API key (for Google Gemini API)
- Required Python packages: `openai`, `python-dotenv`

## Setup

1. Clone this repository
2. Create a `.env` file with your API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```
3. Install required packages:
   ```
   pip install openai python-dotenv
   ```

## Usage

Run the agent using:
```
python try.py
```

Example commands:
- "Create a simple React app" (uses non-interactive mode)
- "Build a Flask API with two endpoints"
- "Add a login component to my React app"
- "Create a MongoDB connection in my Node.js app"

## Example Session

```
> Create express js application
🧠: The user wants to create an Express.js application. This involves creating a directory for the project, initializing npm, installing the express package, creating a server file, and adding a start script to the package.json.
🔨 Executing: command_exec
🔑 mkdir express-app && cd express-app && npm init -y
...

> can you please create a route /app in my server.js file when user redirect to it it shows hello world
🧠: The user wants to add a new route `/app` to the existing `server.js` file, which will display 'Hello World' when accessed.
🔨 Executing: read_file
...
🔨 Executing: write_file
...
💬: Added a new route `/app` to the `server.js` file. Accessing `/app` will now display 'Hello World!'
```

## Features

- **Project Generation**: Creates complete project structures with appropriate files
- **Code Writing**: Generates code for both frontend and backend components
- **Command Execution**: Runs necessary commands for installation, building, etc.
- **Code Analysis**: Understands existing code to make appropriate modifications
- **File Operations**: Creates, reads, updates, and deletes files as needed

## Tools

The agent has the following tools at its disposal:
- `command_exec`: Executes terminal commands
- `read_file`: Reads file contents to understand context
- `write_file`: Creates or updates files with content
- `scan_directory`: Lists files in a directory
- `analyze_code`: Analyzes existing code structure
