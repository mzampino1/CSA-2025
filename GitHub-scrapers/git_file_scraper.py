from github import Github
import re
import pandas as pd
import json

cfg = json.load(open("credentials.json"))
cfg_app = cfg["app"]

gitToken = cfg_app["github_token"]

pattern = r"[a-zA-Z0-9/_]+\.(?:py|js|html|java)"
token = gitToken

gh = Github(token)
me = gh.get_user()

# could make the path a varible and feed it the path if we made this a function
repo = gh.get_repo("vitorfs/parsifal") 

# Copy list of file links
def get_all_files(repo, path=""):
    contents = repo.get_contents(path)
    files = []
    for content_file in contents:
        if content_file.type == "dir":
            files += get_all_files(repo, content_file.path)
        else:
            if re.search(pattern, content_file.path) and not content_file.path.endswith("__init__.py"):
                raw_url = f"https://raw.githubusercontent.com/{repo.full_name}/master/{content_file.path}"
                raw_url = raw_url.replace(" ", "%20")  # Replace spaces with %20
                print("Found file:", raw_url)
                files.append(raw_url)
    return files

file_name = input("Please enter the name of your output .txt file (without .txt):\n")

file_links = get_all_files(repo)

with open(f"C:\\Users\\Smatt\\Desktop\\CSA Summer 2025\\CSA-2025\\input\\{file_name}.txt", "w") as output:
    for link in file_links:
        output.write(link + "\n")



""" # (  We can use the subject lines to look for things that we do not want, i.e. README edits, editorconfic, etc. )

    subject = commit.commit.message.splitlines()[0]   
    language = commit.language
    if "Fix search scopus results rendering when there is no data" in subject: 
        print(subject)
        body    = "\n".join(commit.commit.message.splitlines()[1:])
        print(body)
"""
print(me.login, me.name)

# Return the sha, pre sorted as source code, changes in a github link format to feed to chat