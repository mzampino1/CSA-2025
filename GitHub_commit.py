# These are the functions that involve pushing commits to GitHub.

import re
import git
import requests
import os
import shutil

class GitHubCommits:

    def __init__(self, repo_path, links):
        self.repo_path = repo_path
        self.links = links

    def clear_repo_folder(self, folder_name):
        repo = git.Repo(self.repo_path)
        folder_path = os.path.join(self.repo_path, folder_name)
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        # Stage the deletions
        repo.git.add(folder_path)
        # Commit the deletions
        repo.index.commit(f"Clear contents of {folder_name} folder")
        # Push the commit
        repo.remote(name='origin').push()
        print(f"Cleared and committed deletions in '{folder_name}' for repo at {self.repo_path}.")

    # Changes the content of a file to the new code provided.
    def change_file(file_path, new_code):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_code)
        print(f"File {file_path} has been updated with new code.")

    def commit_code(self, file_path, new_code, message):

        repo = git.Repo(self.repo_path)

        # Change the file content to the new code
        GitHubCommits.change_file(file_path, new_code)
        
        # Add the file to the staging area
        repo.index.add([file_path])
        
        # Commit the changes
        repo.index.commit(message)

        # Push the changes to the remote repository
        origin = repo.remote(name='origin')
        origin.push()
        
        print(f"Changes committed and pushed to {repo.remotes.origin.url}")

        # Return the commit SHA
        return repo.head.commit.hexsha

    def commit_new_file(self, file_link):
        # Extract the file name from the link
        file_name = file_link.split('/')[-1]
        
        # Get the file content
        response = requests.get(file_link)
        if response.status_code == 200:
            new_code = response.text
            file_path = f"{self.repo_path}\\files\\{file_name}"

            # Commit the new code to the repository
            return self.commit_code(file_path, new_code, f"Add non-vulnerable file: {file_name}")
        else:
            print(f"Failed to get {file_name}: {response.status_code}")
            return None

    def commit_text_file(self, file_path, message):
        repo = git.Repo(self.repo_path)
        repo.index.add([file_path])
        repo.index.commit(message)
        repo.remote(name='origin').push()
        print(f"Committed and pushed changes to {repo.remotes.origin.url}")
        return repo.head.commit.hexsha

    def remove_file(self, file_path):
        repo = git.Repo(self.repo_path)
        repo.index.remove([file_path])
        repo.index.commit(f"Remove file: {file_path}")
        repo.remote(name='origin').push()
        print(f"Removed and committed deletions for {file_path}.")
    
    def make_nonVCC_commits(self, links):
        file_names = []
        with open(self.repo_path + "\\non_vcc.txt", "w") as f:
            for link in links:
                file_name = link.split("/")[-1]
                f.write(file_name + ": " + self.commit_new_file(link) + "\n")
                file_names.append(file_name)
        return file_names
    
    # Extracts the code block from the LLM's answer.
    # Returns the code as a string, or None if not found.
    # Also returns the CWE ID if present in the answer.
    def extract_vulnerable_code(answer):
        # This regex looks for a code block (```...```)
        match = re.search(
            r"```(?:python|html|java|javascript)\s+(.*?)```",
            answer,
            re.DOTALL | re.IGNORECASE
        )
        # Look for CWE-, return following number
        if match:
            cwe_match = re.search(r"CWE-(\d+)", answer)
            if cwe_match:
                return match.group(1).strip(), cwe_match.group(1)
        return None, None

    # Commits the new code to GitHub, creating a vulnerability-contributing commit hash
    def commit_answers(self, results):
        with open(self.repo_path + "\\vcc.txt", "w") as f:
            for result in results:
                vul_code, cwe_id = GitHubCommits.extract_vulnerable_code(result["answer"])
                if(vul_code):
                    if cwe_id is None:
                        cwe_id = "Unknown CWE ID"
                    f.write(result["file_name"] + f" (CWE-{cwe_id})" + ": " + self.commit_code(self.repo_path + "\\files\\" + result["file_name"], vul_code, f"Make {result["file_name"]} vulnerable") + "\n")
                else:
                    # Remove corresponding non-vcc file if no vulnerable code is found in answer
                    self.remove_file(self.repo_path + "\\files\\" + result["file_name"])
                    # Remove non-vcc hashes from non_vcc.txt
                    with open(self.repo_path + "\\non_vcc.txt", "r") as non_vcc_file:
                        lines = non_vcc_file.readlines()
                    with open(self.repo_path + "\\non_vcc.txt", "w") as non_vcc_file:
                        for line in lines:
                            if result["file_name"] not in line:
                                non_vcc_file.write(line)
                    print(f"Error on file {result["file_name"]}: no vulnerable code generated.")