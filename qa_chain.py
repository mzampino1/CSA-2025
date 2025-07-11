from langchain.prompts import PromptTemplate
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_ollama import OllamaLLM
from transformers import AutoTokenizer



class LangchainQA_Chain(): 
    def __init__(self, similarChunks, HUGGINGFACE_HUB_TOKEN):
        self.similarChunks = similarChunks
        self.HUGGINGFACE_HUB_TOKEN = HUGGINGFACE_HUB_TOKEN

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

        # Initialize tokenizer for your LLM model
        self.tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-70b-Instruct-hf", token = self.HUGGINGFACE_HUB_TOKEN)
        self.MAX_TOKENS = 2048  # adjust to your model's context window


        def combine_docs(docs, **kwargs):
            """Join docs, truncate to MAX_TOKENS."""
            context_str = "\n".join(doc.page_content for doc in docs)
            tokens = self.tokenizer.encode(context_str)
            if len(tokens) > self.MAX_TOKENS:
                tokens = tokens[:self.MAX_TOKENS]
                context_str = self.tokenizer.decode(tokens)
            return context_str

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=self.similarChunks.as_retriever(search_type="similarity", k=3),
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt, "combine_documents_chain_kwargs": {"combine_documents_func": combine_docs}},
            return_source_documents=False, 
            verbose= True
        )
        return qa_chain
