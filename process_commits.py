import os
import time
import logging
import requests
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List


class ProcessCommits:
    def __init__(
        self,
        repo_path,
        file_names,
        links: List[str],
        similar_chunks,
        HUGGINGFACE_HUB_TOKEN,
        github_token: str,
        num_gpus: int = 4,
        ): 
        self.file_names = file_names
        self.links = links
        self.similar_chunks = similar_chunks
        self.github_token = github_token
        self.num_gpus = num_gpus
        self.HUGGINGFACE_HUB_TOKEN = HUGGINGFACE_HUB_TOKEN
        self.repo_path = os.path.expanduser(repo_path)


        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
        )

    def _worker(self, commit_link,file_name, device_index=4):
        os.environ["CUDA_VISIBLE_DEVICES"] = str(device_index)
        from qa_chain import LangchainQA_Chain 

        logging.info(f"[GPU {device_index}] Starting {commit_link}")

        qa_chain = LangchainQA_Chain(self.similar_chunks, self.HUGGINGFACE_HUB_TOKEN).build_QA_Chain_with_langchain()

        resp = ""

        file_path = os.path.join(self.repo_path, "files", file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            resp = f.read()

        raw_patch = resp
        query = raw_patch
   

        with open("selected_context.log", "a") as f:
            # Tries to complete the RAG three times, then fails if nothing is generated on the
            # 3rd attempt
            for i in range(3): 
                try: 
                    result = qa_chain.invoke(query)
                    docs_str = "\n\n".join(str(doc) for doc in result["source_documents"])
                    f.write(f"\n\nInput File Name: {file_name}\n\n" + docs_str)
                    break 
                except Exception as e: 
                    if i == 2:
                        logging.error(f"Error in QA chain: {e}")
            answer = result.get("result") if isinstance(result, dict) else result

        return f"\n\nFile Name: {file_name}\n\n" + answer

    def run(self) -> List[str]:

        tasks = [
            (link, idx % self.num_gpus)
            for idx, link in enumerate(self.links)
        ]
        results = []

        with ProcessPoolExecutor(max_workers=self.num_gpus) as pool:
            futures = {
                pool.submit(self._worker, self.repo_path, file_name): 
                file_name for file_name in self.file_names
            }
            for fut in as_completed(futures):
                link = futures[fut]
                try:
                    out = fut.result()
                    results.append({"file_name": link, "answer": out})
                    print(f" Finished {link}")
                except Exception as e:
                    print(f" Exception on {link}: {e}")

        return results

