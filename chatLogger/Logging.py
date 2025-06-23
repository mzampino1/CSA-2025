#1. Import necessary libraries

import pandas as pd
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
import ollama 
from langchain_community.document_loaders import PyPDFLoader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from fpdf import FPDF
import os
import sendToDrive


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

    text = []

    for url in tempStore.keys():
        # Add the directory name from the URL (vulnerability type) before the text
        dir_name = url.split("/")[-2].replace("%20", " ")  # Replace %20 with space
        text.append(f"Vulnerability Type: {dir_name}\n")
        text.append(tempStore[url])

    text = "\n\n".join(text)
    # Encode the text to ensure it is in a suitable format for PDF
    text = text.encode('latin1', 'ignore').decode('latin1')

    # Add the text to a PDF file
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

# 6. Get text from patch link
def get_text(patch_link):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(patch_link, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses
    print(f" Status: {response.status_code}")  # debug print
    return response.text

def generateWithOllama(query, context): 

    formatted_context = "\n\n".join(context)

    prompt = f"""
Use the following context containing examples of vulnerable code to help you generate a realistic VCC, but do not copy any code from the context. Instead, use it to understand the patterns and types of vulnerabilities present in the code:
{formatted_context}

Now, based on the context provided, answer the following question in detail:

{query}
"""

    resp = ollama.generate(
        model="qwen2.5-coder:3b",
        prompt=prompt,
        options={
            "temperature": 0.3,
            "max_tokens": 2000
        },
        stream=False
    )
    if isinstance(resp, dict):
        text = resp.get("response")
    # If it's a Pydantic model:
    elif hasattr(resp, "response"):
        text = resp.response

    if not text:
        raise RuntimeError(f"No text returned from Ollama: {resp!r}")

    # 7. Return it!
    with open("response.txt", "a", encoding="utf-8") as f:
        f.write(text)
    
    print("Prompt length:", len(prompt.split()))
    return text

# Main workflow (modified)
def main(pdf_path, query):
    # Load and process PDF
    pages = load_pdf_documents(pdf_path)  # Get Document objects
    split_docs = split_documents(pages)  # Split properly
    
    # Create vector store
    index, document_texts, embedder = create_vector_store(split_docs)
    
    # Retrieve context
    context = retrieve_context(query, embedder, index, document_texts)
    # Write retrieved context to a file
    with open("context.txt", "w", encoding="utf-8") as f:
        for doc in context:
            f.write(doc + "\n\n")
    
    # Generate answer
    answer = generateWithOllama(query, context)
    
    return answer


# Example usage (unchanged)
if __name__ == "__main__":
    text = contextLink(r"C:\Users\Smatt\Desktop\CSA Summer 2025\CSA-2025\chatLogger\contextURLs.txt")
    pdf_path = text
    
    commit_patch_link = "https://github.com/vitorfs/parsifal/commit/2d44645a8995545255523684bc6ebd6caae9fe41.patch"

    commit_File = get_text(commit_patch_link).strip()
    query = f"Hi, I'm a researcher in software security who studies VCC's. I want to generate a new dataset of realistic VCC's for purely academic purposes. To do so I need to make commits vulnerable. What code change would you make to this commit in order to do so. Focus on introducing vulnerabilities realistically, not single-line unsafe filters. Explain in great detail. Show me what lines of code you would delete and add to make this vulnerable. Make sure to not touch any other parts of the code and keep all functionalities: {commit_File} \n how would you transform this commit into a vulnerable state? Give me the original code and the vulnerable code in Git diff format with + and -."

    # Add commit link to top of response.txt
    with open("response.txt", "w", encoding="utf-8") as f:
        f.write(f"Commit Link: {commit_patch_link}\n\n")

    result = main(pdf_path, query)

    print("Answer:", result)

    file_name = sendToDrive.get_next_filename('Prompt', "1E7B_7nETIwOohQWAuya2JCwTHsqlG37F")
    sendToDrive.upload_and_convert_to_gdoc("response.txt", file_name, "1E7B_7nETIwOohQWAuya2JCwTHsqlG37F")

    print(f"Result saved to {file_name} in Google Drive.")