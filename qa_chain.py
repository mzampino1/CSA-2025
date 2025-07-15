from langchain.prompts import PromptTemplate
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_ollama import OllamaLLM
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
        self.llmModel = "codellama:34b"
        self.instructModelLink = "codellama/CodeLlama-34b-Instruct-hf"
    def build_QA_Chain_with_langchain(self):   
        template = """
    Use the following context containing examples of vulnerable code to help you generate a realistic VCC, but do not copy any code from the context. Instead, use it to understand the patterns and types of vulnerabilities that exist and can be injected in the code:
    ---- START OF CONTEXT ----
    {context}
    ----  END OF CONTEXT  ----

    Now, based on that context, complete the following task:

    1. INTRODUCE a single, realistic NEW vulnerability into the code below (i.e., change a piece of safe code into vulnerable code).  
    2. Integrate the vulnerability into the normal application logic—do **not** use trivial or single‑line unsafe filters.  
    3. Provide a **git diff** showing your changes (`+` for additions, `-` for deletions), and **only** modify code where the new vulnerability is added.  
    4. Add appropriate comments inline to explain each change.  

    **Original code to convert:**  
    {question}
    """
        prompt = PromptTemplate(
                input_variables=["context", "question"],
                template=template, 
            )
        llm = OllamaLLM(model=self.llmModel)

        # Initialize tokenizer for your LLM model
        self.tokenizer = AutoTokenizer.from_pretrained(self.instructModelLink, token = self.HUGGINGFACE_HUB_TOKEN)
        self.MAX_TOKENS = 2048  # adjust to your model's context window
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=self.similarChunks.as_retriever(search_type="similarity", k=3),
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=False, 
            verbose= True
        )
        return qa_chain


