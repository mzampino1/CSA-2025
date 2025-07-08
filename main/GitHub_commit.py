# These are the functions that involve pushing commits to GitHub.

import re
import git
import requests

# Extracts the code block from the LLM's answer.
# Returns the code as a string, or None if not found.
def extract_vulnerable_code(answer):
    # This regex looks for a code block (```...```)
    match = re.search(
        r"```(?:python|html|java|javascript)\s+(.*?)```",
        answer,
        re.DOTALL | re.IGNORECASE
    )
    if match:
        return match.group(1).strip()
    return None

# Changes the content of a file to the new code provided.
def change_file(file_path, new_code):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_code)
    print(f"File {file_path} has been updated with new code.")

def commit_code(file_path, new_code, message):
    
    repo = git.Repo(r"C:\Users\Smatt\Desktop\CSA Summer 2025\CSA-2025-Dataset")
    
    # Change the file content to the new code
    change_file(file_path, new_code)
    
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

def commit_new_file(file_link):
    # Extract the file name from the link
    file_name = file_link.split('/')[-1]
    
    # Get the file content
    response = requests.get(file_link)
    if response.status_code == 200:
        new_code = response.text
        file_path = f"C:\\Users\\Smatt\\Desktop\\CSA Summer 2025\\CSA-2025-Dataset\\files\\{file_name}"

        # Commit the new code to the repository
        return commit_code(file_path, new_code, f"Add non-vulnerable file: {file_name}")
    else:
        print(f"Failed to get {file_name}: {response.status_code}")
        return None