from github import Github
import re

# get github token from credentials.json
import json

with open("credentials.json", "r") as f:
    credentials = json.load(f)
    gitToken = credentials["app"]["github_token"]

pattern = r"[a-zA-Z0-9/_]+\.(?:py|js|html|java)"
token = gitToken

gh = Github(token)
me = gh.get_user()

# Change this to the repository you want to scrape files from
repo = gh.get_repo("vitorfs/parsifal") 

# Copy list of file links
def get_all_files(repo, path=""):
    contents = repo.get_contents(path)
    files = []
    for content_file in contents:
        if content_file.type == "dir":
            files += get_all_files(repo, content_file.path)
        else:
            # Check if the file matches the pattern, is not an __init__.py file, and is not empty (has non-whitespace content)
            if re.search(pattern, content_file.path) and not content_file.path.endswith("__init__.py") and content_file.size > 0:
                file_contents = content_file.decoded_content.decode("utf-8")
                if file_contents.strip():
                    raw_url = f"https://raw.githubusercontent.com/{repo.full_name}/master/{content_file.path}"
                    raw_url = raw_url.replace(" ", "%20")  # Replace spaces with %20
                    print("Found file:", raw_url)
                    files.append(raw_url)
    return files

file_name = input("Please enter the name of your output .txt file (without .txt):\n")

file_links = get_all_files(repo)

with open(f"input\\{file_name}.txt", "w") as output:
    for link in file_links:
        output.write(link + "\n")

print(me.login, me.name)