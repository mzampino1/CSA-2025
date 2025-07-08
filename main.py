from config_loader import ConfigLoader
from context_loader import ContextLoader
from vector_store import VectorStoreManager
from qa_chain import LangchainQA_Chain
from process_commits import ProcessCommits
from drive_upload import UploadToDrive
import logging

def main(): 
    config = ConfigLoader("credentials.json")

    contextLoader = ContextLoader(config.context_file_path, config.github_token)
    contextLoader.load_context_url()
    contextLoader.transform_into_raw_url()
    contextLoader.get_context_parallel()
    contextLoader.create_context_info()
    chunks = contextLoader.split_context()

    similarChunks = VectorStoreManager(chunks).create_vector_store()

    qa_chain = LangchainQA_Chain(similarChunks).build_QA_Chain_with_langchain()
    _1_dfs = qa_chain.invoke("warmup")

    processCommits = ProcessCommits(config.input_links, qa_chain, config.github_token)
    answers = processCommits.process_parallel_commit()
    logging.info(f"Total answers generated: {len(answers)}")

    uploadToDrive = UploadToDrive(answers, config.drive_folder_id)
    uploadToDrive.upload_answers()


if __name__ == '__main__':
    main()