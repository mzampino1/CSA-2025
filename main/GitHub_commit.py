# These are the functions that involve pushing commits to GitHub.

import re
import git
import requests

# Extracts the code block under the 'Vulnerable Code' section from the LLM's answer.
# Returns the code as a string, or None if not found.
def extract_vulnerable_code(answer):
    # This regex looks for 'Vulnerable Code:' followed by a code block (```...```)
    match = re.search(
        r"Vulnerable Code:\s*```(?:\w*\n)?(.*?)```",
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
    
    repo = git.Repo('.')
    
    # Change the file content to the new vulnerable code
    change_file(file_path, new_code)
    
    # Add the file to the staging area
    repo.index.add([file_path])
    
    # Commit the changes
    repo.index.commit(message)

    # Push the changes to the remote repository
    origin = repo.remote(name='origin')
    origin.push()
    
    print(f"Changes committed and pushed to {repo.remotes.origin.url}")

def add_file_commit(file_links):
    for file_link in file_links:
        # Extract the file name from the link
        file_name = file_link.split('/')[-1]
        
        # Download the file content (assuming the link is a direct link to the raw file)
        response = requests.get(file_link)
        if response.status_code == 200:
            new_code = response.text
            
            # Commit the new code to the repository
            commit_code(file_name, new_code, f"Add {file_name}")
        else:
            print(f"Failed to download {file_name}: {response.status_code}")