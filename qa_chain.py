from langchain.prompts import PromptTemplate
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_ollama import OllamaLLM
#from transformers import LlamaTokenizer
from transformers import AutoTokenizer



class CombineDocsFunc:
    def __init__(self, tokenizer, max_tokens=2048):
        self.tokenizer = tokenizer
        self.max_tokens = max_tokens
    def __call__(self, docs, **kwargs):
        context_str = "\n".join(doc.page_content for doc in docs)
        tokens = self.tokenizer.encode(context_str)
        if len(tokens) > self.max_tokens:
            tokens = tokens[:self.max_tokens]
            context_str = self.tokenizer.decode(tokens)
        return context_str



class LangchainQA_Chain(): 
    def __init__(self, similarChunks, HUGGINGFACE_HUB_TOKEN):
        self.similarChunks = similarChunks
        self.HUGGINGFACE_HUB_TOKEN = HUGGINGFACE_HUB_TOKEN
        self.llmModel = "krith/qwen2.5-coder-32b-instruct"
        self.instructModelLink = "Qwen/qwen2.5-coder-32b-instruct"
    def build_QA_Chain_with_langchain(self):   
        template = """
    Use the following context containing examples of vulnerable code to help you generate a realistic VCC, but do not copy any code from the context. Instead, use it to understand the patterns and types of vulnerabilities that exist and can be injected in the code:
    ----START OF CONTEXT
    {context}
    ----END OF CONTEXT

    Now, based on the context provided, answer the following question in detail:

    INTRODUCE a realistic NEW vulnerability to the code that will be provided. As in change safe code to vulnerable code.
    Integrate it naturally into the existing flow. NO trivial one line “hacks”. If you use any new modules, be sure to import them.
    In a section titled \"CWE-## Vulnerable Code\" (fill in the CWE ID in this exact format), give me the entire modified file (with a comment indicating where the vulnerability is).
    **THIS is my original code file that I want to be converted into vulnerable code: **
    {question}
    ** END **
    Only modify the code where you are adding the NEW vulnerability, print the rest of the code the same as I gave you above. 
    """
        prompt = PromptTemplate(
                input_variables=["context", "question"],
                template=template, 
            )
        llm = OllamaLLM(model=self.llmModel)

                      # Initialize tokenizer for your LLM model
        self.tokenizer = AutoTokenizer.from_pretrained(self.instructModelLink, trust_remote_code=True, use_fast=False, token = self.HUGGINGFACE_HUB_TOKEN)
        #self.tokenizer = LlamaTokenizer.from_pretrained("hf-internal-testing/llama-tokenizer")
        self.MAX_TOKENS = 2048  # adjust to your model's context window
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=self.similarChunks.as_retriever(search_type="similarity", search_kwargs={"k":3}),
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True, 
            verbose= True
        )
        return qa_chain


