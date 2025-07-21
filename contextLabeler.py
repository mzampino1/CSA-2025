from langchain_ollama import OllamaLLM
import requests

class ContextLabeler():
    def __init__(self):
        with open("input-text/contextURLs.txt", "r") as f: 
            self.links = f.read().splitlines()

    def ollamaSetup(self): 
        llm = OllamaLLM(model ="qwen2.5-coder:3b")
        for links in self.links: 
            contextFile = requests.get(links, headers={"User-Agent": "Mozilla/5.0"})
            response = llm.invoke(f"Read this file: {contextFile.text} --- Now determine if it is a vulnerable code example. If it is then label where that vulnerability exists by ONLY ADDDING COMMENTS AND LABELING THE VULNERABILITY / EXPLAINING IT. DO NOT EDIT ANY CODE. However, if it is not a vulnerable code example, simply respond with NO")
            if response != "NO": 
                with open("output-text/temp.txt", "w") as f: 
                    f.write(response)
            else: 
                print(f"{links} is not a vulnerable code example")

if __name__ == "__main__":
    contextLabeler = ContextLabeler()
    contextLabeler.ollamaSetup()
