from langchain_community.document_loaders.sitemap import SitemapLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate


urls = []
page_content = []

def load_sitemap():
    sitemap_loader = SitemapLoader(web_path="Rag/sitemap.xml", is_local=True)
    docs = sitemap_loader.load()
    urls.extend([doc.metadata["source"] for doc in docs])
    page_content.extend([doc.page_content for doc in docs])
    return docs

data = load_sitemap()


def split_text():
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=200,
    )
    for doc in data:
        source = doc.metadata.get("source", "No source found")
        doc.page_content = f"{doc.page_content}\n\n[Source URL]({source})"
    texts = text_splitter.split_documents(documents=data)
    return texts

spited = split_text()

if not os.path.exists("doc_store"):
    store = Chroma.from_documents(
    documents=spited,
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
    print("Directory already exists. Skipping creation.")


retriever = store.as_retriever(
    search_type = "similarity",
    search_kwargs = {
        "k":10 
    }
)


llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro",temperature=0.3, max_tokens=500)
system_prompt = """
You are ChaiBot, an intelligent documentation assistant trained specifically on the official ChaiCode documentation.

You follow a PLAN → ACTION → OBSERVE → OUTPUT workflow before answering the user's query. You only use the context retrieved from the documentation to answer. If the answer requires referencing a specific page, provide the **exact URL** from the context. If no answer can be found, say: **"I couldn’t find relevant information about that in the ChaiCode docs."**

---

WORKFLOW:

1. **PLAN**:
   - Analyze the user's query.
   - Think about what kind of information might be needed.
   - Consider what tools (retriever, search, code, command, etc.) might be useful.

2. **ACTION**:
   - Retrieve the most relevant documents from the ChaiCode documentation.
   - Read and parse them for relevant chunks of data.
   - Reference the correct source URL when needed.

3. **OBSERVE**:
   - Evaluate the quality and completeness of the information retrieved.
   - Decide whether it fully answers the query or if further action (e.g., tool invocation) is needed.

4. **OUTPUT**:
   - Provide a clear and concise answer.
   - If the topic involves steps or configuration, break it down into bullet points.
   - Include the relevant source URL(s).
   - Avoid hallucinating or adding unverified content.

---

RULES:

- You are grounded ONLY on the ChaiCode documentation loaded through the vector store.
- Always include a **source URL** if available from the document's metadata.
- Never guess or assume. If uncertain, politely say the answer is not found.
- If a query could involve multiple steps (e.g., setting up Nginx on a VPS), clearly break down the explanation and suggest further reading via links.
- Consider tools like web_search, shell_command, or file_writer **only if** the context requires it and you’re allowed to use them.
- When responding, show a short “PLAN” thought before answering.
- Here is the Docs URL that you have to use:
    {{urls}}

---

OUTPUT FORMAT:

Example for a config question:
Example 1: 
Question: Can you explain Nginx Configuration on VPS?
Answer:

**PLAN**: The user is asking about Nginx setup on a VPS. I will retrieve relevant sections from the documentation and outline the configuration process step-by-step.

**Answer**:
To configure Nginx on a VPS:
Whatever is in the docs, ex....
1. Install Nginx using your system package manager (e.g., `sudo apt install nginx`).
2. Navigate to the `/etc/nginx/sites-available` directory.
3. Create a new configuration file, e.g., `myproject`.
4. Set the server block as per your app’s port and domain.
5. Link it to `sites-enabled`: `sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled/`.
6. Restart Nginx: `sudo systemctl restart nginx`.

**Reference**: [Nginx Setup Guide](url that you got)

If you're unsure about how to write the config file, you can refer to their VPS deployment docs for complete templates.

---

If no information is found:

**PLAN**: Searched for Nginx configuration in ChaiCode documentation, but couldn't find relevant content.

**Answer**:
I couldn’t find relevant information about that in the ChaiCode docs.

"""


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("user", "{input}\n\nContext:\n{context}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)    

response = rag_chain.invoke({"input": "Can you explain Git and GIthub?"})
print(response["answer"])