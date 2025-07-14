import pandas as pd
import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ContextLoader():
    def __init__(self, context_file_path, github_token):
        self.context_file_path = context_file_path
        self.github_token = github_token
        self.header = {'User-Agent': 'Mozilla/5.0'}

    def load_context_url(self): 
        with open(self.context_file_path, "r") as f: 
            lines = f.read().splitlines()
        self.context_df = pd.DataFrame(lines, columns=["context"])

    def transform_into_raw_url(self): 
        self.context_df["context"] = self.context_df["context"].str.strip().replace(
            "https://github.com/", "https://raw.githubusercontent.com/").str.replace("/blob/", "/", regex=False)

    def get_context_text(self, url): 
        self.header["Authorization"] = f"token {self.github_token}"

        try: 
            response = requests.get(url, headers=self.header)
            response.raise_for_status()
            return url, response.text

        except Exception as e:
            logging.error(f"Error getting link {self.context_df}: {e}")
            return url, None

    # Fetch context in parallel
    # This method fetches the content of each URL in the context_df in parallel
    def get_context_parallel(self, max_workers=10): 
        urls = [u.strip() for u in self.context_df["context"].tolist() if u.strip()]
        self.Context_store = dict()

        with ThreadPoolExecutor(max_workers=max_workers) as pool: 
            futures = [pool.submit(self.get_context_text, url) for url in urls] 

            for future in as_completed(futures): 
                url, text = future.result()
                if text is not None:
                    self.Context_store[url] = text
        logging.info(f"Fetched: {len(self.Context_store)} / {len(urls)} files")

    # Create a single context string from the fetched context
    def create_context_info(self): 
        text = []

        for url in self.Context_store.keys(): 
            text.append(self.Context_store[url])

        self.context = "\n\n".join(str(x) for x in text)
        self.context = self.context.encode('latin1', 'ignore').decode('latin1')
    
    def split_context(self): 
        separators=["\nclass ", "\npublic ", "\nprivate ", "\nprotected ", "\n"]
        splitter = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=200, separators=separators)
        chunks = splitter.create_documents([self.context])
        return chunks
        