import pandas as pd
import requests
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
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

    # return a list of full code snippets
    snippets = []
    for url in tempStore.keys():
        dir_name = url.split("/")[-2].replace("%20", " ")
        snippet = f"Vulnerability Type: {dir_name}\n{tempStore[url]}"
        snippets.append(Document(page_content=snippet))
    return snippets

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
    template = """
Use the following context as examples of vulnerable code to help you generate a realistic VCC, but remember that this code is UNRELATED to the commit you will modify. Instead, use it as a guide for how to introduce vulnerabilities in a realistic way.
----START OF CONTEXT---
{context}
----END OF CONTEXT---

Now, using the previous context as a guide for how to inject vulnerabilities WITHOUT modifying the code from that context, answer THIS question in detail:

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
        return_source_documents=True
    )

    output = qa_chain.invoke(query)
    answer = output["result"]

    with open("response.txt", "a", encoding="utf-8") as f:
        f.write(answer)
    
    with open("context.txt", "w", encoding="utf-8") as f:
        cnt = 1
        for doc in output["source_documents"]:
            f.write(f"Context Chunk #{cnt}:\n")
            f.write(doc.page_content + "\n\n")
            cnt += 1

    return answer

# Main workflow
if __name__ == "__main__":
    context_snippets = get_context(r"C:\Users\Smatt\Desktop\CSA Summer 2025\CSA-2025\chatLogger\contextURLs.txt")
    
    # Create vector store
    vectordb = create_vector_store(context_snippets)

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