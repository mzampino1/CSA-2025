# Files for Notre Dame's Summer 2025 Computing Skills Accelerator Program

## Folder Descriptions

### GitHub-scrapers
Contains scripts to scrape data from GitHub repositories:  
git_file_scraper.py - Retrieves URLs for relevant files from a GitHub repository and stores them in contextURLs.txt  
git_patch_scraper.py - Retrieves URLs for relevant commit patch files from a GitHub repository and stores them in CommitLinks.txt  
  
### input
Contains text files relevant to the program's input data:  
contextURLs.txt - context file URLs found by git_file_scraper.py to be used in the program  
inputLinks.txt - file URLs of the files found by git_file_scraper.py to be made vulnerable by the program  

### main
Contains the main program's python files:  
config_loader.py - loads information from credentials.json  
context_loader.py - gets context code from links and splits the code into chunks to be used in vector search  
drive_upload.py - uploads answers to Google Drive  
GitHub_commit.py - commits the non-vulnerable code and the vulnerable code to create a non-VCC and a VCC  
main.py - the main workflow of the program, which calls methods from the other files  
process_files.py - generates vulnerable versions of the input files using the LLM  
qa_chain.py - initializes the question-answering chain that is used to perform retrieval-augmented generation  
vector_store.py - creates vector store representing context to be used in vector search  
