from langchain_community.document_loaders.sitemap import SitemapLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

class ChaiBot:
    def __init__(self):
        print("Initializing ChaiBot...")
        self.client = OpenAI(
            api_key=os.getenv("GOOGLE_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        self.system_prompt = """
You are ChaiBot, an intelligent documentation assistant trained specifically on the official ChaiCode documentation.


You work in a START → PLAN → ANALYZE → RETRIEVE → SYNTHESIZE → OUTPUT workflow when answering user queries.
You ONLY use the context retrieved from the ChaiCode documentation to answer questions.

If the answer requires referencing a specific page, provide the exact URL from the context.
If no relevant information is found, say: "I couldn't find relevant information about that in the ChaiCode docs"

When answering:
- Use the exact content from the documentation rather than summarizing or paraphrasing it, especially for code examples, step-by-step instructions, and technical details.
- Always strive to provide clear, complete, and detailed explanations.
- Do not skip steps in your thinking or your output — be explicit and provide thorough reasoning at each stage.
- If multiple parts of the documentation are relevant, combine them carefully and maintain all context and structure.
- If the answer requires referencing a specific page, provide the exact URL from the documentation context.
- If the code is available than add the code also.
- If no relevant information is found, say: "I couldn't find relevant information about that in the ChaiCode docs."

WORKFLOW:

1. PLAN:
- Analyze the user's query carefully.
- Break down complex questions into simpler components.
- Identify key concepts and terms that need to be addressed.
- Break down query in a step back prompting and chain of thought process.

2. ANALYZE:
- Look through the retrieved context.
- Identify the most relevant pieces of information.
- Find other relevant information that might be related to the query.
- Consider how different documents might relate to each other and if required use multiple documents to answer the query.

3. RETRIEVE:
- Identify and extract the exact content from documentation that answers the query.
- When code examples exist in the documentation, include them exactly as they appear.
- Extract all URLs that might be useful for citations.
- Preserve the original structure and formatting of the documentation wherever possible.

4. SYNTHESIZE:
- Use the exact content from the documentation as much as possible.
- Maintain the original organization, headings, and structure from the documentation.
- Only synthesize information if multiple documents need to be combined.
- Do NOT rewrite or paraphrase documentation content unless absolutely necessary.

5. OUTPUT:
- Reproduce the exact content from the documentation as your primary response.
- Keep the original section headings, code formatting, and examples intact.
- If content spans multiple documents, clearly indicate where each part comes from.
- Always include source URLs.

RULES:
- Base your answers only on the ChaiCode documentation context provided.
- Reproduce the exact content from the documentation whenever possible, especially code examples.
- Never guess or make up information. If uncertain, say the answer is not found.
- Preserve original formatting, code blocks, and examples exactly as they appear in the documentation.
- Prioritize verbatim content from the documentation over your own explanations.
- Always follow JSON format for output.

IMPORTANT: You must respond using only the following JSON format:

{
"step": "<one of: plan, analyze, retrieve, synthesize, output>",
"content": "<your response content here>"
}

Never include anything outside this JSON. No explanations, no extra formatting, no markdown.

WORKFLOW EXAMPLES:

Example 1:
User query: "How do I use Git branches?"

Output:
{
    "step": "plan",
    "content": "User wants to know about Git branches. I'll find documentation about Git branches."
}

Output:
{
    "step": "analyze",
    "content": "I found documentation about Git branches that explains what they are and how to use them."
}

Output:
{
    "step": "retrieve",
    "content": "The documentation explicitly covers Git branches in detail here: - https://chaidocs.vercel.app/youtube/chai-aur-git/branches/" 
}

Output:
{
    "step": "synthesize",
    "content": "I'll extract the exact content from the documentation about Git branches, preserving all examples, headings, and formatting."
}

Output:
{
    "step": "output",
    "content": {{Exact content from the documentation}}
}

Example 2:
User query: "What is blockchain?"

Output:
{
    "step": "plan",
    "content": "The user wants information about blockchain technology. I need to search for relevant documentation."
}

Output:
{
    "step": "analyze",
    "content": "After searching through the available documentation, I don't see any specific articles about blockchain technology."
}

Output:
{
    "step": "retrieve",
    "content": "No relevant information found."
}

Output:
{
    "step": "synthesize",
    "content": "Since there's no information about blockchain in the ChaiCode documentation, I'll inform the user."
}

Output:
{
    "step": "output",
    "content": {{Exact content from the documentation}}
}
"""
        
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        self.context = ""
        
        print("Setting up vector store and retriever...")
        self.retriever = self.setup_retriever()
        print("ChaiBot initialization completed.")
    
    def load_sitemap(self):
        print("Loading sitemap...")
        sitemap_loader = SitemapLoader(web_path="Rag/sitemap.xml", is_local=True)
        docs = sitemap_loader.load()
        
        urls = [doc.metadata["source"] for doc in docs]
        page_content = [doc.page_content for doc in docs]
        
        print(f"Loaded {len(docs)} documents from sitemap")
        return docs
    
    def split_text(self, data):
        print("Splitting text into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 200
        )
        for doc in data:
            source = doc.metadata.get("source", "No source found")
            
            # Extract a title from the URL
            title_segment = source.strip("/").split("/")[-1]
            title = title_segment.replace("-", " ").title()

            doc.page_content = f"{doc.page_content}\n\n[{title}]({source})"
            
        texts = text_splitter.split_documents(documents=data)
        print(f"Split into {len(texts)} chunks")
        return texts
    
    def setup_retriever(self):
        data = self.load_sitemap()
        splitted = self.split_text(data)
        
        if not os.path.exists("doc_store"):
            print("Creating new Chroma DB...")
            store = Chroma.from_documents(
                documents=splitted,
                embedding=GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
                persist_directory="doc_store",
                collection_name="docs"
            )
            print("New Chroma DB created.")
        else:
            store = Chroma(
                embedding_function=GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
                persist_directory="doc_store",
                collection_name="docs"
            )
            print("Existing Chroma DB loaded.")
                    
        retriever = store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 10, 
                "fetch_k": 20,  
                "lambda_mult": 0.7,
            }
        )

        return retriever
    
    def get_context_for_query(self, query):
        print(f"🔍 Retrieving context for: {query}")
        docs = self.retriever.invoke(query)
        context = "\n\n".join([doc.page_content for doc in docs])
        print(f"Retrieved {len(docs)} relevant documents")
        return context
    
    def process_response(self, content):
        """Format the response for better readability"""
        if "step" in content and "content" in content:
            step = content["step"].lower()
            step_content = content["content"]
            
            if step == "plan":
                return f"🧠 PLANNING: {step_content}"
            elif step == "analyze":
                return f"🔍 ANALYZING: {step_content}"
            elif step == "retrieve":
                return f"📚 RETRIEVING: {step_content}"
            elif step == "synthesize":
                return f"🧩 SYNTHESIZING: {step_content}"
            elif step == "output":
                return f"\n📝 ANSWER:\n{step_content}"
        
        return content
    
    def run(self):
        print("\n" + "=" * 60)
        print("🚀 ChaiBot Documentation Assistant 🚀")
        print("=" * 60)
        print("\nA RAG-powered assistant for ChaiCode documentation")
        print("\nType 'exit' to quit the assistant")
        print("=" * 60 + "\n")
        
        try:
            while True:
                query = input("➤ Ask about ChaiCode docs: ")
                
                if query.lower() in ["exit", "quit"]:
                    print("\n👋 Goodbye! ChaiBot Documentation Assistant is shutting down.")
                    break
                
                context = self.get_context_for_query(query)
                self.messages.append({
                    "role": "user", 
                    "content": query
                })
                self.messages.append({
                    "role": "assistant", 
                    "content": f"Relevant ChaiCode documentation context:\n\n{context}"
                })
                
                conversation_active = True
                current_step = None
                
                print("\n⏳ Processing your query...\n")
                
                while conversation_active:
                    try:
                        response = self.client.chat.completions.create(
                            model="gemini-2.0-flash",
                            response_format={"type": "json_object"},
                            messages=self.messages,
                        )
                        
                        try:
                            response_content = response.choices[0].message.content


                            parsed_output = json.loads(response_content)
                            
                            self.messages.append({
                                "role": "assistant",
                                "content": response_content
                            })
                            
                            step = parsed_output.get("step", "").lower()
                            
                            if step != current_step:
                                current_step = step
                                formatted_output = self.process_response(parsed_output)
                                print(formatted_output)
                            
                            if step == "output":
                                conversation_active = False
                            
                        except json.JSONDecodeError:
                            print("❌ Error: Invalid JSON response from API")
                            print(f"Raw response: {response_content[:100]}...")
                            conversation_active = False
                            
                    except Exception as e:
                        print(f"❌ Error: {str(e)}")
                        conversation_active = False
                
                print("\n" + "-" * 60 + "\n")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye! ChaiBot Documentation Assistant is shutting down.")

if __name__ == "__main__":
    bot = ChaiBot()
    bot.run()