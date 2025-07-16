from langchain.prompts import PromptTemplate
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_ollama import OllamaLLM



class LangchainQA_Chain(): 
    def __init__(self, similarChunks):
        self.similarChunks = similarChunks

    def build_QA_Chain_with_langchain(self):   
        template = """
    You may use the following context containing examples of vulnerable code to help you generate a realistic vulnerability, but DO NOT COPY ANY CODE FROM THIS. Instead, use it to understand the patterns and types of vulnerabilities that exist and can be injected in the code:
    ----START OF CONTEXT
    {context}
    ----END OF CONTEXT

    Now, based on the context provided, answer the following question in detail:

    INTRODUCE a realistic NEW vulnerability to the code that will be provided. As in change safe code to vulnerable code,
    in which untrusted input meaningfully affects control flow, data integrity, or security-sensitive operations. If you use any new modules, be sure to import them.
    In a section titled \"CWE-## Vulnerable Code\" (fill in the CWE ID in this exact format), give me the entire modified file.
    THIS is my original code file that I want to be converted into vulnerable code: 
    {question}
    Use the context only for inspiration and pattern recognition. Do NOT copy and paste any code from the context. All code you generate MUST make a change to the original file above (with a comment indicating where the vulnerability is).
    COPY ALL OF THE ORIGINAL CODE TO BE MODIFIED except where you are adding the new vulnerability. Do not remove or replace any existing code unless strictly necessary for the vulnerability.
    """
        prompt = PromptTemplate(
                input_variables=["context", "question"],
                template=template, 
            )
        # This can be set to any Ollama model you want to use
        llm = OllamaLLM(model="qwen2.5-coder:3b")

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            # Finds the most similar chunks to the prompt
            retriever=self.similarChunks.as_retriever(search_type="similarity", search_kwargs={"k": 3}),
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True, 
            verbose= True
        )
        return qa_chain
