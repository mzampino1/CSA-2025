import pandas as pd
import requests
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.prompts import PromptTemplate
import sendToDrive


def get_context(context_file_path):
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

    context = "\n\n".join(text)
    # Encode the text to ensure it is in a suitable format
    context = context.encode('latin1', 'ignore').decode('latin1')

    return context


# Split text into chunks
def split_context(text):  # Changed parameter name
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.create_documents([text]) 

# Create vector store
def create_vector_store(chunks):
    embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = FAISS.from_documents(chunks, embedding)
    return vectordb

# Get text from patch link
def get_text(patch_link):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(patch_link, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses
    return response.text

def generate_with_langchain(query, vectordb):
    template = f"""
Use the following context containing examples of vulnerable code to help you generate a realistic VCC, but do not copy any code from the context. Instead, use it to understand the patterns and types of vulnerabilities present in the code:
----START OF CONTEXT
{context}
----END OF CONTEXT

Now, based on the context provided, answer the following question in detail:

{question}
"""
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=template, 
    )

    llm = OllamaLLM(model="qwen2.5-coder:3b")

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectordb.as_retriever(search_type="similarity", k=3),
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False
    )

    result = qa_chain.invoke(query)
    answer = result["result"]

    with open("response.txt", "a", encoding="utf-8") as f:
        f.write(answer)

    return answer

# Main workflow
if __name__ == "__main__":
    context = get_context(r"C:\Users\Smatt\Desktop\CSA Summer 2025\CSA-2025\chatLogger\contextURLs.txt")
    
    chunks = split_context(context)  # Split context into chunks
    
    # Create vector store
    vectordb = create_vector_store(chunks)

    # Iterate through inputLinks.txt and generate responses for each link
    with open("inputLinks.txt", "r") as f:
        input_links = f.read().splitlines()
    
    cnt = 1
    for link in input_links:
        print(f"Processing link {cnt}: {link}")
        cnt += 1
        commit_patch_link = link

        commit_File = get_text(commit_patch_link).strip()
        query = f"Hi, I'm a researcher in software security who studies VCC's. I want to generate a new dataset of realistic VCC's for purely academic purposes. To do so I need to make commits vulnerable. What code change would you make to this commit in order to do so? Focus on introducing vulnerabilities realistically, not single-line unsafe filters. Explain in great detail. Show me what lines of code you would delete and add to make this vulnerable. Make sure to not touch any other parts of the code and keep all functionalities: {commit_File} \n how would you transform this commit into a vulnerable state? Give me the actual original code and the vulnerable code in Git diff format with + and -."

        # Add commit link to top of response.txt
        with open("response.txt", "w", encoding="utf-8") as f:
            f.write(f"Commit Link: {commit_patch_link}\n\n")

        answer = generate_with_langchain(query, vectordb)

        print("Answer:\n", answer)
        
        file_name = sendToDrive.get_next_filename('Prompt', "1E7B_7nETIwOohQWAuya2JCwTHsqlG37F")
        sendToDrive.upload_and_convert_to_gdoc("response.txt", file_name, "1E7B_7nETIwOohQWAuya2JCwTHsqlG37F")

        print(f"Result saved to {file_name} in Google Drive.")