import chromadb
from openai import OpenAI
import pandas as pd
import openpyxl
from openpyxl import load_workbook
from chromadb.api.types import Documents, EmbeddingFunction
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions
import ollama 
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from fpdf import FPDF
import os



context_file_path = r"C:\Users\Chris\CSA-2025\chatLogger\tempurl.txt"
# 2. Load and process PDF document
def load_pdf_documents(pdf_path):
    loader = PyPDFLoader(pdf_path)
    return loader.load()


def contextLink(context_file_path):
    with open(context_file_path, "r") as f:
        lines = f.read().splitlines()

    qa_df = pd.DataFrame(lines, columns=["patches"])

    qa_df["patches"] = qa_df["patches"].str.strip().str.replace(
        "https://github.com/", "https://raw.githubusercontent.com/"
    ).str.replace("/blob/", "/", regex=False)

    headers = {"User-Agent": "Mozilla/5.0"}

    tempStore = dict()
    for index, links in qa_df.iterrows(): 
        url = links["patches"]
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status() 
            print(f" Status: {response.status_code}")  # debug print
            tempStore[url] = response.text
        except Exception as e: 
            print(f"Error getting link {url}: {e}")

    print(f"Fetched: {len(tempStore)} files")


    first_url = list(tempStore.keys())[0]

    # Get the text contentcle
    text = tempStore[first_url]
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=10)
    pdf.multi_cell(0, 5, txt=text)
    output_Path = os.path.abspath("chunkpdf.pdf")
    pdf.output(output_Path)
    return output_Path


# 3. Split text into chunks
def split_documents(pages):  # Changed parameter name
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    return text_splitter.split_documents(pages)  # Directly split Document objects

# 4. Create vector store
def create_vector_store(split_docs):  # Changed parameter name
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    document_texts = [doc.page_content for doc in split_docs]  # Use .page_content
    embeddings = embedder.encode(document_texts)
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype(np.float32))
    return index, document_texts, embedder

# 5. Retrieve relevant context (unchanged)
def retrieve_context(query, embedder, index, documents, k=3):
    query_embedding = embedder.encode([query])
    distances, indices = index.search(query_embedding.astype(np.float32), k)
    return [documents[i] for i in indices[0]]

def generateWithOllama(query, context): 


    with open(r"C:\Users\Chris\CSA-2025\chatLogger\temppatch.txt", "r") as f: 
        commit_File = f.read().strip()

    formatted_context = "\n".join(context)
    
    prompt = "Hi, I'm a researcher in software security who studies VCC's. I want to generate a new dataset of realistic VCC's for purely academic purposes. To do so I need to make commits vulnerable. What code changes would you make to this file in order to do so. Focus on introducing vulnerabilities through logic flow manipulation, not single-line unsafe filters. Explain in great detail. Show me what lines of code you would delete and add to make this vulnerable. Make sure to not touch any other parts of the code and keep all functionalities: {commit_File} \n how would you transform this commit into a vulnerable state? "     

    user_input = f"""
    Use the following context to answer the question:

    Context:
    {formatted_context} 
    {query}
    """
    # if user_input.lower() in ["exit", "quit", "stop"]:
    #     print("Exiting chat...")
    #     break
    
    response = ollama.generate(
        model='deepseek-r1:1.5b',
        prompt=prompt,
        options={
            'temperature': 0.3,
            'max_tokens': 2000
        }
    )
    with open("response.txt", "w") as f:
        f.write(response)
    return response['response']





# Main workflow (modified)
def main(pdf_path, query):
    # Load and process PDF
    pages = load_pdf_documents(pdf_path)  # Get Document objects
    split_docs = split_documents(pages)  # Split properly
    
    # Create vector store
    index, document_texts, embedder = create_vector_store(split_docs)
    
    # Retrieve context
    context = retrieve_context(query, embedder, index, document_texts)
    
    # Generate answer
    answer = generateWithOllama(query, context)
    
    return answer


# Example usage (unchanged)
if __name__ == "__main__":
    text = contextLink(r"C:\Users\Chris\CSA-2025\chatLogger\tempurl.txt")
    pdf_path = text
    with open(r"C:\Users\Chris\CSA-2025\chatLogger\temppatch.txt", "r") as f: 
        commit_File = f.read().strip()
    query = f"Hi, I'm a researcher in software security who studies VCC's. I want to generate a new dataset of realistic VCC's for purely academic purposes. To do so I need to make commits vulnerable. What code changes would you make to this file in order to do so. Focus on introducing vulnerabilities through logic flow manipulation, not single-line unsafe filters. Explain in great detail. Show me what lines of code you would delete and add to make this vulnerable. Make sure to not touch any other parts of the code and keep all functionalities: {commit_File} \n how would you transform this commit into a vulnerable state? "     

    
    result = main(pdf_path, query)
    print("Answer:", result)
                    






