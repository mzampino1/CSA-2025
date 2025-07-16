from github import Github
import re
import pandas as pd
import time
from datetime import datetime
from github import RateLimitExceededException

# get github token from credentials.json
import json

with open("credentials.json", "r") as f:
    credentials = json.load(f)
    gitToken = credentials["app"]["github_token"]

pattern = r"[a-zA-Z0-9/_]+\.(?:java)"
token = gitToken

gh = Github(token)
me = gh.get_user()

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

def get_file_links_from_csv(df, gh):
    # Iterate through each row to get file links for the commit
    for idx, row in df.iterrows():
        try:
            repo_full_name = row["project"]
            commit_hash = row["hash"]

            # Check and handle rate limit
            rate_limit = gh.get_rate_limit().core
            if rate_limit.remaining == 0:
                reset_time = rate_limit.reset
                sleep_time = (reset_time - datetime.now()).total_seconds()
                print(f"Rate limit hit. Sleeping for {sleep_time:.0f} seconds...")
                time.sleep(sleep_time + 1)

            repo = gh.get_repo(repo_full_name)
            commit = repo.get_commit(commit_hash)
            files = commit.files  # List of files modified by this commit

            print(f"Commit: {commit_hash} in {repo_full_name}")
            raw_urls = []
            for file in files:
                # Get the raw link to the file as it exists in this commit
                raw_url = f"https://raw.githubusercontent.com/{repo_full_name}/{commit_hash}/{file.filename}"
                raw_urls.append(raw_url)

        except RateLimitExceededException:
            rate_limit = gh.get_rate_limit().core
            reset_time = rate_limit.reset
            sleep_time = (reset_time - datetime.now()).total_seconds()
            print(f"Rate limit exceeded exception caught. Sleeping for {sleep_time:.0f} seconds...")
            time.sleep(sleep_time + 1)
            continue

        except Exception as e:
            print(f"Error processing commit {commit_hash} in {repo_full_name}: {e}")
            continue

    return raw_urls


# Write raw URLs to a txt file
with open("input/raw_input_urls.txt", "w") as f:
    for url in get_file_links_from_csv("new_non_vccs.csv"):
        f.write(url + "\n")

get_file_links_from_csv(pd.read_csv("new_non_vccs.csv"), gh)

print(me.login, me.name)