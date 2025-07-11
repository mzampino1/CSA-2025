import os
import logging

from config_loader import ConfigLoader
from context_loader import ContextLoader
from vector_store import VectorStoreManager
from process_commits import ProcessCommits
from drive_upload import UploadToDrive
import multiprocessing

def main():
    # 1) Basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s"
    )

    # 2) Load config & GitHub token
    config = ConfigLoader("credentials.json")
    gh_token = config.github_token

    # 3) Build your context and vector store
    context_loader = ContextLoader(config.context_file_path, gh_token)
    context_loader.load_context_url()
    context_loader.transform_into_raw_url()
    context_loader.get_context_parallel()
    context_loader.create_context_info()
    chunks = context_loader.split_context()
    similar_chunks = VectorStoreManager(chunks).create_vector_store()

    # 4) Parallel commit processing over 4 GPUs
    processor = ProcessCommits(
        links=config.input_links,
        similar_chunks=similar_chunks,
        HUGGINGFACE_HUB_TOKEN = config.HUGGINGFACE_HUB_TOKEN,
        github_token=gh_token,
        num_gpus=4,              # spawn 4 processes ? 4 A10s
    )
    answers = processor.run()
    logging.info(f"Total answers generated: {len(answers)}")

    # 5) Upload to Drive
    uploader = UploadToDrive(answers, config.drive_folder_id)
    uploader.upload_answers()

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    main()
