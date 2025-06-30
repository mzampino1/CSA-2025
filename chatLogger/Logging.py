import pandas as pd
import requests
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.prompts import PromptTemplate
import sendToDrive
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
logging.basicConfig(level=logging.INFO)

def load_config(fileinfo): 
    cfg = json.load(open(fileinfo))
    app_cfg = cfg["app"]
    CONTEXT_FILE_PATH = app_cfg["context_file_path"]
    INPUT_LINKS_FILE = app_cfg["input_links_file"]
    DRIVE_FOLDER_ID = app_cfg["drive_folder_id"]
    GITHUB_TOKEN = app_cfg["github_token"]
    return CONTEXT_FILE_PATH, INPUT_LINKS_FILE, DRIVE_FOLDER_ID, GITHUB_TOKEN

def get_context_url(context_file_path): 
    with open(context_file_path, "r") as f: 
        lines = f.read().splitlines()
    context_df = pd.DataFrame(lines, columns=["context"])
    return context_df

def transform_into_raw_url(context_df): 
    context_df["context"] = context_df["context"].str.strip().replace(
        "https://github.com/", "https://raw.githubusercontent.com/").str.replace("/blob/", "/", regex=False)
    return context_df

def get_context_text(raw_URLs,github_token, header = {'User-Agent': 'Mozilla/5.0'}): 
    header["Authorization"] = f"token {github_token}"

    try: 
        response = requests.get(raw_URLs, headers=header)
        response.raise_for_status()
        return raw_URLs, response.text
    
    except Exception as e:
        print(f"Error getting link {raw_URLs}: {e}")
        return raw_URLs, None


def get_context_parallel(raw_URLs, github_token, max_workers=10, header = {'User-Agent': 'Mozilla/5.0'}): 
    urls = [u.strip() for u in raw_URLs["context"].tolist() if u.strip()]
    Context_store = dict()

    with ThreadPoolExecutor(max_workers=max_workers) as pool: 
        futures = [pool.submit(get_context_text, url, github_token) for url in urls] 

        for future in as_completed(futures): 
            url, text = future.result()
            if text is not None:
                Context_store[url] = text
    print(f"Fetched: {len(Context_store)} / {len(urls)} files")
    return Context_store



def create_context_info(context_Store_text): 
    text = []

    for url in context_Store_text.keys(): 
        vul_type = url.split("/")[-1].replace("%20", " ")
        text.append(f"Vulnearbility Type: {vul_type}\n")
        text.append(context_Store_text[url])

    context = "\n\n".join(str(x) for x in text)
    context = context.encode('latin1', 'ignore').decode('latin1')

    return context

def split_context(context): 
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
    chunks = splitter.create_documents([context])
    return chunks
    
def create_vector_store(chunks, embeddingsModel = "all-MiniLM-L6-v2"): 
    embedding = HuggingFaceEmbeddings(model_name= embeddingsModel)
    similarChunks = FAISS.from_documents(chunks, embedding)
    return similarChunks

def get_NonVCC_text(patch, header = {'User-Agent': 'Mozilla/5.0'}): 
    _input = requests.get(patch, headers=header)
    _input.raise_for_status()
    return _input.text


def build_QA_Chain_with_langchain( similarChunks):   
    template = """
Use the following context containing examples of vulnerable code to help you generate a realistic VCC, but do not copy any code from the context. Instead, use it to understand the patterns and types of vulnerabilities that exist and can be injected in the code:
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
        retriever=similarChunks.as_retriever(search_type="similarity", k=3),
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False, 
        verbose= True
    )
    return qa_chain

def process_commit(commit_url, qa_chain, drive_folder_id, response_path, github_token):
    # raw_patch = get_context_text([commit_url], github_token)[commit_url].strip()
    raw_patch = requests.get(commit_url, headers= {
        "User-Agent": "Mozilla/5.0",
        "Authorization": f"token {github_token}"
    })

    
    query = (
        "INTRODUCE a realistic NEW vulnerability to the code provided. As in change safe code to vulnerable code."
        "DO so in a flow type way such as what you see in the context, not single-line unsafe filters. "
        "Explain in detail and provide a git diff with + and - of how you made the code vulnerable: "
        f"This is my original code that I want to be converted into a vulnerable code commit: {raw_patch.text}"
        "Only modify the code where you are adding the NEW vulnerabilities."
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

def process_parallel_commit(links, qa_chain, drive_folder_id, github_token): 
    max_workers = 2

    with ThreadPoolExecutor(max_workers=max_workers) as pool: 
        future_to_link = {pool.submit(process_commit, link, qa_chain, drive_folder_id, "response.txt", github_token,): 
                          link for link in links}
        for future in as_completed(future_to_link):
            link = future_to_link[future]
            try:
                answer = future.result()
                print(f"✅ Finished {link}")
            except Exception as e:
                print(f"❌ Error on {link}: {e}")

def main(context_file_path, input_links_file, drive_folder_id, github_token): 
    raw_urls = get_context_url(context_file_path)
    raw_urls = transform_into_raw_url(raw_urls)
    patches = get_context_parallel(raw_urls, github_token)
    context = create_context_info(patches)
    chunks = split_context(context)
    similarChunks = create_vector_store(chunks)
    qa_chain = build_QA_Chain_with_langchain(similarChunks)
    _ = qa_chain.invoke("warmup")


    with open(input_links_file, 'r', encoding='utf-8') as f:
        links = [l.strip() for l in f if l.strip()]

    process_parallel_commit(links, qa_chain, drive_folder_id, github_token)

if __name__ == '__main__':
    context_file_path, input_links_file, drive_folder_id, github_token = load_config("credentials.json")
    main(
        context_file_path= context_file_path,
        input_links_file= input_links_file,
        drive_folder_id= drive_folder_id,
        github_token= github_token
    )
