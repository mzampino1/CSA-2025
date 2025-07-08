import requests
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed


class ProcessCommits(): 
    def __init__(self, links,  qa_chain, github_token):
        self.qa_chain = qa_chain
        self.links = links
        self.github_token = github_token

    def process_commit(self, commit_link):
        # raw_patch = get_context_text([commit_url], github_token)[commit_url].strip()
        raw_patch = requests.get(commit_link, headers= {
            "User-Agent": "Mozilla/5.0",
            "Authorization": f"token {self.github_token}"
        })

        
        query = (
            "INTRODUCE a realistic NEW vulnerability to the code provided. As in change safe code to vulnerable code."
            "DO so in a flow type way such as what you see in the context, not single-line unsafe filters. "
            "Explain in detail and provide a git diff with + and - of how you made the code vulnerable: "
            f"This is my original code that I want to be converted into a vulnerable code commit: {raw_patch.text}"
            "Only modify the code where you are adding the NEW vulnerabilities."
        )

        for i in range(3): 
            try: 
                result = self.qa_chain.invoke(query)
                time.sleep(2)
                break 
            except Exception as e: 
                if i == 2:
                    logging.error(f"Error in qa_chain.invoke: {e}")
        answer = result.get("result") if isinstance(result, dict) else result

        return f"Commit Link: {commit_link}\n\n" + answer

    def process_parallel_commit(self): 
        answers = []
        
        max_workers = 2

        with ThreadPoolExecutor(max_workers=max_workers) as pool: 
            future_to_link = {pool.submit(self.process_commit, link): 
                            link for link in self.links}
            for future in as_completed(future_to_link):
                link = future_to_link[future]
                try:
                    answer = future.result()
                    answers.append(answer)
                    logging.info(f"✅ Finished {link}")
                except Exception as e:
                    logging.info(f"❌ Error on {link}: {e}")
        return answers
