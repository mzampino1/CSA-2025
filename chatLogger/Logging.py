import pandas as pd
import requests
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.prompts import PromptTemplate
import sendToDrive



def get_context_url(context_file_path): 
    with open(context_file_path, "r") as f: 
        lines = f.read().splitlines()
    context_df = pd.DataFrame(lines, columns=["context"])
    return context_df

def transform_into_raw_url(context_df): 
    context_df["context"] = context_df["context"].str.strip().replace(
        "https://github.com/", "https://raw.gitbubusercontent.com/").str.replace("/blob/", "/", regex=False)
    return context_df

def get_context_text(raw_URLs, header = {'User-Agent': 'Mozilla/5.0'}): 
    context_Store_text = dict()
    for index, row in raw_URLs.itterows(): 
        url = row["context"]
        try: 
            response = requests.get(url, headers=header)
            response.raise_for_status()
            context_Store_text[url] = response.text
        except Exception as e:
            print(f"Error getting link {url}: {e}")

    print(f"Fetched: {len(raw_URLs)} files")
    return context_Store_text

def create_context_info(context_Store_text): 
    text = []

    for url in context_Store_text.keys(): 
        vul_type = url.split("/")[-2].replace("%20", " ")
        text.append(f"Vulnearbility Type: {vul_type}\n")
        text.append(context_Store_text[url])

    context = "\n".join(text)
    context = context.encode('latin1', 'ignore').decode('latin1')

    return context

def split_context(context): 
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
    chunks = splitter.create_documents([context])
    return chunks
    
def create_vector_store(chunks, embeddingsModel): 
    if embeddingsModel is None: 
        embeddingsModel = "all-MiniLM-L6-v2"
    embedding = HuggingFaceEmbeddings(model_name= embeddingsModel)
    similarChunks = FAISS.from_documents(chunks, embedding)
    return similarChunks

def get_NonVCC_text(patch, header = {'User-Agent': 'Mozilla/5.0'}): 
    response = requests.get(patch, headers=header)
    response.raise_for_status()
    return response.text

def build_QA_Chain_with_langchain(query, similarChunks, vectordb): 
    
    template = f"""
Use the following context containing examples of vulnerable code to help you generate a realistic VCC, but do not copy any code from the context. Instead, use it to understand the patterns and types of vulnerabilities present in the code:
----START OF CONTEXT
{similarChunks}
----END OF CONTEXT

Now, based on the context provided, answer the following question in detail:

{query}
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
    return qa_chain

def process_commit(commit_url, qa_chain, drive_folder_id, response_path):
    raw_patch = get_context_text([commit_url])[commit_url].strip()
    query = (
        "Hi, I'm a researcher in software security who studies VCC's. "
        "I want to generate a new dataset of realistic VCC's. To do so, make commits vulnerable. "
        "Focus on realistic vulnerabilities, not single-line unsafe filters. "
        "Explain in detail and provide a git diff with + and -: "
        f"{raw_patch}"
    )

    with open(response_path, 'w', encoding='utf-8') as f:
        f.write(f"Commit Link: {commit_url}\n\n")

    result = qa_chain.invoke(query)
    answer = result.get("result") if isinstance(result, dict) else result

    with open(response_path, 'a', encoding='utf-8') as f:
        f.write(answer)

    filename = sendToDrive.get_next_filename('Prompt', drive_folder_id)
    sendToDrive.upload_and_convert_to_gdoc(response_path, filename, drive_folder_id)
    print(f"Result saved to {filename} in Google Drive.")

    return answer

def main(context_file_path, input_links_file, drive_folder_id): 
    raw_urls = get_context_url(context_file_path)
    raw_urls = transform_into_raw_url(raw_urls)
    patches = get_context_text(raw_urls)
    context = create_context_info(patches)
    chunks = split_context(context)
    vectordb = create_vector_store(chunks)
    qa_chain = build_QA_Chain_with_langchain(vectordb)

    with open(input_links_file, 'r', encoding='utf-8') as f:
        links = [l.strip() for l in f if l.strip()]
    for idx, link in enumerate(links, 1):
        print(f"Processing link {idx}/{len(links)}: {link}")
        process_commit(link, qa_chain, drive_folder_id)

if __name__ == '__main__':
    main(
        context_file_path=r"C:\Users\Smatt\Desktop\CSA Summer 2025\contextURLs.txt",
        input_links_file="inputLinks.txt",
        drive_folder_id="1E7B_7nETIwOohQWAuya2JCwTHsqlG37F"
    )
