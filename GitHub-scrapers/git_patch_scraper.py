from github import Github
import re
import pandas as pd
from config_loader import ConfigLoader
import requests

cfg = ConfigLoader("credentials.json")

pattern = r"^[A-Za-z0-9_/\\\.\-]+\.java$"
token = cfg.github_token
cwe_re = re.compile(r"(?i)\bCWE-")
cwe_req = re.compile(r"(?i)\bCWE-\d+\b")


gh = Github(token)
me = gh.get_user()

# could make the path a varible and feed it the path if we made this a function
repo = gh.get_repo("Peanu11/cwe_java_dataset") 



for commit in repo.get_commits():
    sha = commit.sha
    c = repo.get_commit(sha)

    with open(r"C:\Users\Chris\CSA-2025\input-text\contextURLs.txt", "a") as output:
        for f in c.files:
            raw_url = (f.raw_url or "")
            patch = (f.raw_data)
            url = (raw_url)
            data = requests.get(url)
            data.raise_for_status()
            text = data.text
            print(url)
            output.write(f"{url}\n")
            # if cwe_re.search(text):
            #     #print("Found file:", cwe_req.search(text))
            #     #cvalue = str(c).split('"')[1]
            #     print(raw_url)
            #     #output.write("https://raw.githubusercontent.com/Peanu11/cwe_java_dataset/"+str(cvalue)+"/Juliet/1.java\n")      
                



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