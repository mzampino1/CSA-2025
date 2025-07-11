import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

class ProcessFiles(): 
    def __init__(self, file_names, qa_chain, github_token):
        self.qa_chain = qa_chain
        self.file_names = file_names
        self.github_token = github_token

    def process_file(self, repo_path, file_name):
        raw_text = ""
        with open(repo_path + "\\files\\" + file_name, "r") as f:
            raw_text = f.read()

        # The query is only the actual code to ensure the similarity search is as
        # accurate as possible
        query = raw_text

        with open("selected_context.log", "a") as f:
            # Tries to complete the RAG three times, then fails if nothing is generated on the
            # 3rd attempt
            for i in range(3): 
                try: 
                    result = self.qa_chain.invoke(query)
                    docs_str = "\n\n".join(str(doc) for doc in result["source_documents"])
                    f.write(f"Input File Name: {file_name}\n\n" + docs_str)
                    break 
                except Exception as e: 
                    if i == 2:
                        logging.error(f"Error in QA chain: {e}")
            answer = result.get("result") if isinstance(result, dict) else result

            return f"\n\nFile Name: {file_name}\n\n" + answer

    def process_parallel_file(self, repo_path): 
        results = []
        
        max_workers = 2

        with ThreadPoolExecutor(max_workers=max_workers) as pool: 
            future_to_file_name = {pool.submit(self.process_file, repo_path,file_name): 
                          file_name for file_name in self.file_names}
        for future in as_completed(future_to_file_name):
            file_name = future_to_file_name[future]
            try:
                answer = future.result()
                results.append({"file_name": file_name, "answer": answer})
                print(f"✅ Finished {file_name}")
            except Exception as e:
                print(f"❌ Error on {file_name}: {e}")
        return results