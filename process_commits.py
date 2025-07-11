import os
import time
import logging
import requests
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List

from qa_chain import LangchainQA_Chain 


class ProcessCommits:
    def __init__(
        self,
        links: List[str],
        similar_chunks,
        HUGGINGFACE_HUB_TOKEN,
        github_token: str,
        num_gpus: int = 4,
        ): 
        
        self.links = links
        self.similar_chunks = similar_chunks
        self.github_token = github_token
        self.num_gpus = num_gpus
        self.HUGGINGFACE_HUB_TOKEN = HUGGINGFACE_HUB_TOKEN

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
        )

    def _init_chain(self):

        return LangchainQA_Chain(self.similar_chunks, self.HUGGINGFACE_HUB_TOKEN)\
            .build_QA_Chain_with_langchain()

    def _worker(self, commit_link: str, device_index: int):
        os.environ["CUDA_VISIBLE_DEVICES"] = str(device_index)
        logging.info(f"[GPU {device_index}] Starting {commit_link}")

        qa_chain = self._init_chain()

        resp = requests.get(
            commit_link,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Authorization": f"token {self.github_token}",
            },
            timeout=10,
        )
        resp.raise_for_status()
        raw_patch = resp.text

        query = (
            "INTRODUCE a realistic NEW vulnerability to the code provided. As in change safe code to vulnerable code."
            "DO so in a flow type way such as what you see in the context, not single-line unsafe filters. "
            "Explain in detail and provide a git diff with + and - of how you made the code vulnerable: "
            f"This is my original code that I want to be converted into a vulnerable code commit: {raw_patch}"
            "Only modify the code where you are adding the NEW vulnerabilities."
        )

        for attempt in range(3):
            try:
                answer = qa_chain.invoke(query)
                break
            except Exception as e:
                logging.warning(f"[{commit_link}] attempt {attempt+1} failed: {e}")
                time.sleep(2)
        else:
            logging.error(f"[{commit_link}] all retries failed")
            return f"Commit Link: {commit_link}\n\nERROR: failed to process."

        return f"Commit Link: {commit_link}\n\n{answer}"

    def run(self) -> List[str]:

        tasks = [
            (link, idx % self.num_gpus)
            for idx, link in enumerate(self.links)
        ]
        results = []

        with ProcessPoolExecutor(max_workers=self.num_gpus) as pool:
            futures = {
                pool.submit(self._worker, link, dev): link
                for link, dev in tasks
            }
            for fut in as_completed(futures):
                link = futures[fut]
                try:
                    out = fut.result()
                    results.append(out)
                    logging.info(f" Finished {link}")
                except Exception as e:
                    logging.error(f" Exception on {link}: {e}")

        return results

