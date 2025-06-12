from github import Github
from pathlib import Path
import re
import pandas as pd


pattern = "[a-zA-Z0-9/_]+(?=(?:.py|.js))"
with open(r"C:\Users\Smatt\Desktop\MyToken.txt", "r") as f:
    token = f.read().strip()
print(token)

gh = Github(token)
me = gh.get_user()

# could make the path a varible and feed it the path if we made this a function
repo = gh.get_repo("vitorfs/parsifal") 

keywords = {".py", ".js"}

for commit in repo.get_commits():
    sha = commit.sha
    c = repo.get_commit(sha)
    
    for f in c.files:
        patch = (f.patch or "").lower()

        for keyword in keywords:
            if keyword.lower() in patch.lower():
            #if (re.search(pattern, patch.lower())):
                print(f"found {keyword} in diff" , c)
                cvalue = str(c).split('"')[1]
                print("https://github.com/vitorfs/parsifal/commit/"+str(cvalue)+".patch")      
        break

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