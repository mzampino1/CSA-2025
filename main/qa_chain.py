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

    INTRODUCE a realistic NEW vulnerability to the code that will be provided. As in change safe code to vulnerable code.
    Do so in a flow type way such as what you see in the context, not single-line unsafe filters. If you use any new modules, be sure to import them.
    In a section titled \"CWE-## Vulnerable Code\" (fill in the CWE ID in this exact format), give me the entire modified file (with a comment indicating where the vulnerability is).
    THIS is my original code file that I want to be converted into vulnerable code: 
    {question}
    Only modify the code where you are adding the NEW vulnerabilities, but also keep all of the original, unmodified code in that file.
    """
        prompt = PromptTemplate(
                input_variables=["context", "question"],
                template=template, 
            )
        # This can be set to any Ollama model you want to use
        llm = OllamaLLM(model="qwen2.5-coder:3b")

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            # Finds 3 most similar chunks to the prompt
            retriever=self.similarChunks.as_retriever(search_type="similarity", k=3),
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True, 
            verbose= True
        )
        return qa_chain
