from config_loader import ConfigLoader
from context_loader import ContextLoader
from vector_store import VectorStoreManager
from qa_chain import LangchainQA_Chain
from process_files import ProcessFiles
# from drive_upload import UploadToDrive
from GitHub_commit import GitHubCommits
import logging

def main(): 
    config = ConfigLoader("credentials.json")

    # Load context from GitHub URLs and split into chunks for RAG
    contextLoader = ContextLoader(config.context_file_path, config.github_token)
    contextLoader.load_context_url()
    contextLoader.transform_into_raw_url()
    contextLoader.get_context_parallel()
    contextLoader.create_context_info()
    chunks = contextLoader.split_context()
    similarChunks = VectorStoreManager(chunks).create_vector_store()

    # Initialize retrieval QA (question-answering) chain 
    qa_chain = LangchainQA_Chain(similarChunks).build_QA_Chain_with_langchain()
    _1_dfs = qa_chain.invoke("warmup")

    # Clear file for logging the context retrieved
    with open("selected_context.log", "w") as f:
        f.write("")

    commits = GitHubCommits(config.repo_path, config.input_links)
    # Clear the repository folder for non-VCC commits
    commits.clear_repo_folder("files")
    # Perform initial non-VCC commits
    file_names = commits.make_nonVCC_commits(config.input_links)

    # Perform RAG and generate the vulnerable code using the LLM's response
    file_processing = ProcessFiles(file_names, qa_chain, config.github_token)
    results = file_processing.process_parallel_file(commits.repo_path)
    logging.info(f"Total answers generated: {len(results)}")

    # Make VCC commits based on the answers generated
    commits.commit_answers(results)
    commits.commit_csv_file(
        file_path=commits.repo_path + "\\commits.csv",
        message="Add CSV to repository"
    )

    # uploadToDrive = UploadToDrive(answers, config.drive_folder_id)
    # uploadToDrive.upload_answers()


if __name__ == '__main__':
    main()