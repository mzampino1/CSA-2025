from langchain.prompts import PromptTemplate
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_ollama import OllamaLLM
from transformers import AutoTokenizer



def combine_docs( docs, tokenizer, MAX_TOKENS=2048, **kwargs):
    """Join docs, truncate to MAX_TOKENS."""
    context_str = "\n".join(doc.page_content for doc in docs)
    tokens = tokenizer.encode(context_str)
    if len(tokens) > MAX_TOKENS:
        tokens = tokens[:MAX_TOKENS]
        context_str = tokenizer.decode(tokens)
    return context_str



class LangchainQA_Chain(): 
    def __init__(self, similarChunks, HUGGINGFACE_HUB_TOKEN):
        self.similarChunks = similarChunks
        self.HUGGINGFACE_HUB_TOKEN = HUGGINGFACE_HUB_TOKEN
        self.llmModel = "codellama:13b"
        self.instructModelLink = "codellama/CodeLlama-13b-Instruct-hf"
    def build_QA_Chain_with_langchain(self):   
        template = """
    Use the following context containing examples of vulnerable code to help you generate a realistic VCC, but do not copy any code from the context. Instead, use it to understand the patterns and types of vulnerabilities that exist and can be injected in the code:
    ----START OF CONTEXT
    {context}
    ----END OF CONTEXT

    Now, based on the context provided, answer the following question in detail:

    "INTRODUCE a realistic NEW vulnerability to the code provided. As in change safe code to vulnerable code."
    "DO so in a flow type way such as what you see in the context, not single-line unsafe filters. "
    "Explain in detail and provide a git diff with + and - of how you made the code vulnerable: "
    "Only modify the code where you are adding the NEW vulnerabilities."
    "This is my original code that I want to be converted into a vulnerable code commit:"
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
            chain_type_kwargs={"prompt": prompt, "combine_documents_chain_kwargs": {"combine_documents_func": lambda docs, **kwargs: combine_docs(docs, self.tokenizer, self.MAX_TOKENS, **kwargs)}},
            return_source_documents=False, 
            verbose= True
        )
        return qa_chain


