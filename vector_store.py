from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
        

class VectorStoreManager():
    def __init__(self, chunks):
        self.chunks = chunks

    def create_vector_store(self, embeddingsModel = "all-MiniLM-L6-v2"): 
        embedding = HuggingFaceEmbeddings(model_name= embeddingsModel)
        similarChunks = FAISS.from_documents(self.chunks, embedding)
        return similarChunks