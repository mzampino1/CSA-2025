from github import Github
import re
from config_loader import ConfigLoader

config = ConfigLoader("credentials.json")

gitToken = config.github_token

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
            if re.search(pattern, content_file.path) and not content_file.path.endswith("__init__.py"):
                raw_url = f"https://raw.githubusercontent.com/{repo.full_name}/master/{content_file.path}"
                raw_url = raw_url.replace(" ", "%20")  # Replace spaces with %20
                print("Found file:", raw_url)
                files.append(raw_url)
    return files

file_name = input("Please enter the name of your output .txt file (without .txt):\n")

file_links = get_all_files(repo)

with open(f"input-text\\{file_name}.txt", "w") as output:
    for link in file_links:
        output.write(link + "\n")

print(me.login, me.name)