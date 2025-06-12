from github import Github

token = "C:\Users\Chris\OneDrive\Documents\ChatLogger\gitKey"

grubhub = Github(token)
me = grubhub.get_user()

repo = grubhub.get_repo("vitorfs/parsifal") # could make the path a varible in a function

keywords = {".py", ".js"}

for commit in repo.get_commits():
    sha = commit.sha
    c = repo.get_commit(sha)
    
    for f in c.files:
        patch = (f.patch or "").lower()

        for keyword in keywords:
            if keyword.lower() in patch.lower():
              print(f"found {keyword} in diff" , c)

"""
    subject = commit.commit.message.splitlines()[0]
    language = commit.language
    if "Fix search scopus results rendering when there is no data" in subject: 
        print(subject)
        body    = "\n".join(commit.commit.message.splitlines()[1:])
        print(body)
"""
print(me.login, me.name)

# Return the sha, pre sorted as source code changes in a github link format to feed to chat