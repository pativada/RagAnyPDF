# %% [markdown]
# **RAG Any PDF Document Provided
# 
# Customer will provide a document, The RAG will process the document, chunk it and store in the in-memory vector database 
# When customer request a query on specific topic it will address the result
# 

import subprocess

subprocess.run([
    "pip", "install",
    "langchain==0.3.27",
    "langchain-core==0.3.79",
    "langchain-openai==0.3.10",
    "langchain-community==0.3.20",
    "chromadb==0.6.3",
    "pypdf==6.2.0"
])

# %%
#Loading the `config.json` file
import json
import os

# Load the JSON file and extract values
if not os.environ.get("OPENAI_API_KEY") or not os.environ.get("OPENAI_BASE_URL"):

    file_name = 'config.json'
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            config = json.load(file)
            os.environ['OPENAI_API_KEY'] = config.get("OPENAI_API_KEY") # Loading the API Key
            os.environ["OPENAI_BASE_URL"] = config.get("OPENAI_BASE_URL") # Loading the API Base Url
    else:
        # Emergency fallback error if keys are missing in both local and cloud
        raise KeyError(
            "API configuration keys not found! Please set 'OPENAI_API_KEY' "
            "and 'OPENAI_BASE_URL' in your environment variables or config.json."
        )
        
# %%
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')

# %%
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# %%
import io
from pypdf import PdfReader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

def process_pdf_to_documents(bytes_data : bytes, file_name: str):
    # 1. Read PDF from bytes in memory
    if isinstance(bytes_data, str):
        bytes_data = bytes_data.encode("utf-8")

    pdf_stream = io.BytesIO(bytes_data)    
    #print("pdf_stream of 1000:", pdf_stream.getvalue()[:1000], " | Length of pdf_stream: ", len(pdf_stream.getvalue()))  # Debug: Check the type and content of the stream
    # Crucial: Reset the virtual file pointer to the start
    pdf_stream.seek(0)     
    reader = PdfReader(pdf_stream, strict=False)
            # Simple check to see if it worked
    try:            
        if len(reader.pages) == 0:
            return "Error: PDF has no pages."
        
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
        
        # 2. Convert to a LangChain Document
        # metadata is optional but helps track the source
        doc = Document(page_content=full_text, metadata={"source": file_name})
        
        # 3. Split the text into manageable chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=100
        )
        documents = text_splitter.split_documents([doc])
        
        return documents
    
    except Exception as e:
        return f"Failed to read PDF stream: {str(e)}"
# %%


# %%
from langchain.schema import Document
from langchain.vectorstores import Chroma

vectorstore = Chroma(
    collection_name = "CustomerProvidedCollection",
    embedding_function=embeddings)


# %%
def RagAnyPdfFile(query, bytes_data, file_name):

    documents = process_pdf_to_documents(bytes_data, file_name)
    vectorstore.add_documents(documents=documents)

    # 1. Retrieve relevant documents from the vector store
    relevant_docs = vectorstore.similarity_search(query, k=5)
    print("user_query",query, len(query))
    # 2. Combine the retrieved documents into a single context string
    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    
    # 3. Create a prompt for the LLM
    prompt = """You are an autonomous Financial Research Analyst specializing in AI-focused companies.
YOUR PRIMARY GOAL:
Generate a comprehensive financial analysis report for the requested company that includes:
Bring all the important insights by topic by looking at the ###context information provided below.
The response must be very precise to the question provided in the ###Question section.
The context or the doucment processed is provided in the ###Context section. 
###Context:{context}
The user query is provided under the ###Question section. 
###Question:{query}
"""
    prompt = prompt.format(context=context, query=query)
    #prompt = f"Answer the following question based on the provided context:\n\nContext:\n{context}\n\nQuestion: {query}"
    
    # 4. Get the answer from the LLM
    response = llm.invoke(prompt)
    print(prompt)
    return response.content


