# These are the functions that involve pushing commits to GitHub.

import re
import git
import requests
import os
import shutil
import csv


class GitHubCommits:

    def __init__(self, repo_path, repo_owner, links):
        self.repo_path = os.path.expanduser(repo_path)
        self.repo_owner = repo_owner
        self.links = links
        os.makedirs(os.path.join(self.repo_path, "files"), exist_ok=True)

    
    # Checks if a file with the given name already exists in the repository
    # If it does, appends a number to the file name to make it unique
    # Returns the unique file name
    def check_if_file_exists(self, file_name):
        existing_files = os.listdir(os.path.join(self.repo_path, "files"))
        if file_name in existing_files:
            base_name, ext = os.path.splitext(file_name)
            count = 1
            while f"{base_name}-{count}{ext}" in existing_files:
                count += 1
            file_name = f"{base_name}-{count}{ext}"
        return file_name

    def clear_repo_folder(self, folder_name):
                # DEBUG: list out the repo_path contents
        print("DEBUG: repo_path =", self.repo_path)
        try:
            entries = os.listdir(self.repo_path)
            print("DEBUG: contents of repo_path:", entries)
        except Exception as e:
            print("DEBUG: could not list repo_path:", e)

        gitdir = os.path.join(self.repo_path, ".git")
        print("DEBUG: gitdir =", gitdir)
        print("DEBUG: gitdir exists? ", os.path.exists(gitdir))
        print("DEBUG: gitdir isdir? ", os.path.isdir(gitdir))
        if os.path.exists(gitdir) and not os.path.isdir(gitdir):
            # if it�s a file, show its contents
            with open(gitdir, "r") as f:
                print("DEBUG: .git file contents:\n", f.read())

      
        repo = git.Repo(self.repo_path, search_parent_directories=True)
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
    def change_file(self, file_path, new_code):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_code)
        print(f"File {file_path} has been updated with new code.")

    def commit_code(self, file_path, new_code, message):
        print("DEBUG: attempting to open Git repo at:", self.repo_path)

        repo = git.Repo(self.repo_path, search_parent_directories=True)

        # Change the file content to the new code
        self.change_file(file_path, new_code)
        
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
        original_file_name = file_link.split('/')[-1]
        # Ensure unique file name
        file_name = self.check_if_file_exists(original_file_name)
        
        # Get the file content
        response = requests.get(file_link)
        if response.status_code == 200:
            new_code = response.text
            file_path = os.path.join(self.repo_path, "files", file_name)


            # Commit the new code to the repository
            return file_name, self.commit_code(file_path, new_code, f"Add non-vulnerable file: {file_name}")
        else:
            print(f"Failed to get {file_name}: {response.status_code}")
            return None, None

    def commit_csv_file(self, file_path, message):
        repo = git.Repo(self.repo_path, search_parent_directories=True)
        repo.index.add([file_path])
        repo.index.commit(message)
        repo.remote(name='origin').push()
        print(f"Committed and pushed changes to {repo.remotes.origin.url}")
        return repo.head.commit.hexsha

    def remove_file(self, file_path):
        repo = git.Repo(self.repo_path, search_parent_directories=True)
        repo.index.remove([file_path])
        repo.index.commit(f"Remove file: {file_path}")
        repo.remote(name='origin').push()
        print(f"Removed and committed deletions for {file_path}.")
    
    def make_nonVCC_commits(self):
    
        commits_csv = os.path.join(self.repo_path, "commits.csv")

        file_names = []
        # Fill first row of commits.csv with the headers and repository name
        with open(commits_csv, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Repository Name", "File Name", "Non-VCC Commit Hash", "VCC Commit Hash", "CWE ID"])
        with open(commits_csv, "a") as f:
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
                if link != None: 
                    file_name, commit_hash = self.commit_new_file(link)
                    if file_name is None or commit_hash is None:
                        print(f"Failed to commit file from link: {link}")
                        continue
                    writer.writerow([repo_with_owner, file_name, commit_hash, "", ""])
                    file_names.append(file_name)
        return file_names
    
    # Extracts the code block from the LLM's answer.
    # Returns the code as a string, or None if not found.
    # Also returns the CWE ID if present in the answer.
    
    @staticmethod
    def extract_vulnerable_code(answer):
        # 1) Grab the first Java‐fenced code block
        match = re.search(
            r"```(?:java)\s+(.*?)```",
            answer,
            re.DOTALL | re.IGNORECASE
        )
        if not match:
            print(answer)
            return None, None

        code = match.group(1).strip()

        # 2) Find the first CWE marker 
        cwe_match = re.search(r"(?i)cwe[-_\s:]*(\d+)", answer)
        cwe_id = cwe_match.group(1) if cwe_match else None

        return code, cwe_id


    # Commits the new code to GitHub, creating a vulnerability-contributing commit hash
    def commit_answers(self, results):

        commits_csv = os.path.join(self.repo_path, "commits.csv")
        files_dir   = os.path.join(self.repo_path, "files")

        # 1) Load existing CSV into memory
        with open(commits_csv, newline='', encoding='utf-8') as csvfile:
            reader  = csv.reader(csvfile)
            headers = next(reader)
            rows    = [row for row in reader]

        # 2) Update rows based on generated answers
        for result in results:
            file_name    = result.get("file_name")
            answer       = result.get("answer", "")
            vul_code, cwe_id = GitHubCommits.extract_vulnerable_code(answer)

            # Find the matching CSV row
            for idx, row in enumerate(rows):
                if row[1] == file_name:
                    if vul_code:
                        # Commit the vulnerable code and capture its SHA
                        file_path = os.path.join(files_dir, file_name)
                        vcc_hash = self.commit_code(
                            file_path,
                            vul_code,
                            f"Add vulnerable code for {file_name} (CWE-{cwe_id or 'Unknown'})"
                        )
                        row[3] = vcc_hash
                        row[4] = cwe_id or "Unknown CWE ID"
                    else:
                        # No vulnerable code: remove the file and clear row
                        file_path = os.path.join(files_dir, file_name)
                        if os.path.exists(file_path):
                            self.remove_file(file_path)
                        del rows[idx]  # Remove the row
                        print(f"Removed {file_name} from commits.csv as it has no vulnerable code.")
                    break

        # 3) Write updates back to the CSV
        with open(commits_csv, "w", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(rows)

        # 4) Commit & push the updated CSV
        self.commit_csv_file(
            commits_csv,
            "Update VCC commit hashes in commits.csv"
        )

        return rows
