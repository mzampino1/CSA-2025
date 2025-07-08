from langchain.prompts import PromptTemplate
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_ollama import OllamaLLM



class LangchainQA_Chain(): 
    def __init__(self, similarChunks):
        self.similarChunks = similarChunks

    def build_QA_Chain_with_langchain(self):   
        template = """
    Use the following context containing examples of vulnerable code to help you generate a realistic VCC, but do not copy any code from the context. Instead, use it to understand the patterns and types of vulnerabilities that exist and can be injected in the code:
    ----START OF CONTEXT
    {context}
    ----END OF CONTEXT

    Now, based on the context provided, answer the following question in detail:

    {question}
    """
        prompt = PromptTemplate(
                input_variables=["context", "question"],
                template=template, 
            )
        llm = OllamaLLM(model="qwen2.5-coder:3b")

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=self.similarChunks.as_retriever(search_type="similarity", k=3),
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=False, 
            verbose= True
        )
        return qa_chain
