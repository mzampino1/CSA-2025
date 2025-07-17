import re
import git
import requests
import os
import shutil
import csv

class GitHubCommits:
# These are the functions that involve pushing commits to GitHub.
    def __init__(self, repo_path, repo_owner, links):
        self.repo_path = repo_path
        self.repo_owner = repo_owner
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

    def commit_csv_file(self, file_path, message):
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
    
    def make_nonVCC_commits(self):
        file_names = []
        # Fill first row of commits.csv with the headers and repository name
        with open(self.repo_path + "\\commits.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Repository Name", "File Name", "Non-VCC Commit Hash", "VCC Commit Hash", "CWE ID"])
        with open(self.repo_path + "\\commits.csv", "a") as f:
            writer = csv.writer(f)
            
            repo_name = ""
            # If path contains "\\", split using that
            # If it contains "/", split using that
            if "\\" in self.repo_path:
                repo_name = self.repo_path.split("\\")[-1]
            else:
                repo_name = self.repo_path.split("/")[-1]
            repo_with_owner = f"{self.repo_owner}/{repo_name}"

            # For each link, commit the file to the repository
            for link in self.links:
                file_name = link.split("/")[-1]
                commit_hash = self.commit_new_file(link)
                writer.writerow([repo_with_owner, file_name, commit_hash, "", ""])
                file_names.append(file_name)
        return file_names
    
    # Extracts the code block from the LLM's answer.
    # Returns the code as a string, or None if not found.
    # Also returns the CWE ID if present in the answer.
    def extract_vulnerable_code(answer):
        # This regex looks for a code block (```...```)
        match = re.search(
            r"```(.*?)```",
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
        for result in results:
            vul_code, cwe_id = GitHubCommits.extract_vulnerable_code(result["answer"])
            if(vul_code):
                if cwe_id is None:
                    cwe_id = "Unknown CWE ID"

                # Write the VCC commit hash and CWE ID to the commits.csv file
                with open(self.repo_path + "\\commits.csv", "r") as csvfile:
                    lines = csvfile.readlines()
                with open(self.repo_path + "\\commits.csv", "w") as csvfile:
                    for line in lines:
                        if result["file_name"] not in line:
                            csvfile.write(line)
                        else:
                            # Append the VCC commit hash and CWE ID to the line in the CSV file
                            line = line.strip().split(",")
                            line[3] = self.commit_code(
                                self.repo_path + "\\files\\" + result["file_name"],
                                vul_code,
                                f"Add vulnerable code for {result['file_name']} (CWE-{cwe_id})"
                            )
                            line[4] = cwe_id
                            csvfile.write(",".join(line) + "\n")
                            
            else:
                # Remove corresponding non-vcc file if no vulnerable code is found in answer
                self.remove_file(self.repo_path + "\\files\\" + result["file_name"])
                # Remove CSV row with non-vcc hash that has no vulnerable code
                with open(self.repo_path + "\\commits.csv", "r") as csvfile:
                    lines = csvfile.readlines()
                with open(self.repo_path + "\\commits.csv", "w") as csvfile:
                    for line in lines:
                        if result["file_name"] not in line:
                            csvfile.write(line)
                print(f"Error on file {result['file_name']}: no vulnerable code generated.")