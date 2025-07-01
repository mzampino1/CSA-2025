# Files for Notre Dame's Summer 2025 Computing Skills Accelerator Program

## Folder Descriptions

### datasets
Contains initial datasets and their corresponding sources. The C/C++ dataset contains vulnerability-**fixing** commits, and the
Java dataset contains vulnerability-**contributing** commits.

### GitHub-scrapers
Contains scripts to scrape data from GitHub repositories:
git_file_scraper.py - Retrieves URLs for relevant files from a GitHub repository and stores them in contextURLs.txt
git_patch_scraper.py - Retrieves URLs for relevant commit patch files from a GitHub repository and stores them in CommitLinks.txt

### input-text
Contains text files relevant to the program's input data:
CommitLinks.txt - patch file URLs found by git_patch_scraper.py (for storage, not actually accessed by the program)
contextURLs.txt - context file URLs found by git_file_scraper.py to be used in the program
inputLinks.txt - patch file URLs of the commits to be made vulnerable by the program

### output-text
Contains text files relevant to the program's output:
context.txt - context used most recently in the program's RAG (retrieval-augmented generation)

### main
Contains the main program's python files
vulnerability_injection.py - script that performs retrieval-augmented generation and uploads results to Google Drive
drive.py - contains methods to upload files to Google Drive
alternate-versions - folder containing alternate versions of vulnerability_injection.py:
    LangChain_no_chunk.py - similar to original, but gives entire code snippets as context without splitting into chunks
    manual_no_chunk.py - also does not split context, but performs the steps of RAG more manually (without LangChain abstraction)