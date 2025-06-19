import chromadb
from openai import OpenAI
import pandas as pd
import openpyxl
from openpyxl import load_workbook
from chromadb.api.types import Documents, EmbeddingFunction
import requests




book = load_workbook(r"C:\Users\Chris\CSA-2025\chatLogger\vulTestCode.xlsx")



with open(r"C:\Users\Chris\CSA-2025\chatLogger\tempurl.txt", "r") as f:
    lines = f.read().splitlines()

qa_df = pd.DataFrame(lines, columns=["patches"])

qa_df["patches"] = qa_df["patches"].str.strip().str.replace(
    "https://github.com/", "https://raw.githubusercontent.com/"
).str.replace("/blob/", "/", regex=False)

headers = {"User-Agent": "Mozilla/5.0"}

tempStore = dict()
for index, links in qa_df.iterrows(): 
    url = links["patches"]
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() 
        print(f"  ↳ Status: {response.status_code}")  # debug print
        tempStore[url] = response.text
        #chunks = splitter.split_text(tempStore[url])
    except Exception as e: 
        print(f"Error getting link {url}: {e}")

print(f"Fetched: {len(tempStore)} files")


first_url = list(tempStore.keys())[0]

# Get the text contentcle
text = tempStore[first_url]



with open(r"C:\Users\Chris\OneDrive\Documents\ChatLogger\ChatKey.txt", "r") as f:
    api_key = f.read().strip()


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key= str(api_key)
    )

def chat(prompt):   
    response = client.chat.completions.create(
        model="deepseek/deepseek-r1-0528:free",
        messages=[{"role": "user", "content": prompt}
            ]
    )
    return response.choices[0].message.content.strip()

vulTestCode = "https://github.com/alibaba/fastjson/commit/f5903fa56497c00ed0703ac875b511f9bd5f1d8e"



def setup_qa_system(file_path): 
    loader = qa_df.iloc[0]


with open(r"C:\Users\Chris\OneDrive\Documents\ChatLogger\temppatch.txt", "r") as f: 
    commit_File = f.read().strip()


api_key = str(api_key)

class DeepSeekEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key, model="deepseek-embedding"):
        self.api_key = api_key
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.api_url = "https://api.deepseek.com/v1/embeddings"
    
    def __call__(self, texts: Documents) -> list:
        if not texts:
            return []
        
        # Make API call to DeepSeek
        payload = {
            "model": self.model,
            "input": texts
        }
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            raise RuntimeError(f"DeepSeek API Error: {response.status_code} - {response.text}")
        
        result = response.json()
        return [data["embedding"] for data in result["data"]]

# Initialize ChromaDB client
client = chromadb.Client()




context = "" # will be the embeddings.

if __name__ == "__main__":
    while True: 
        #user_input = input("You: ")
        #         
        
        user_input = f"""
        Use the following context to answer the question:

        Context:
        {context} 
        Hi, I'm a researcher in software security who studies VCC's. I want to generate a new dataset of realistic VCC's for purely academic purposes. To do so I need to make commits vulnerable. What code changes would you make to this file in order to do so. Focus on introducing vulnerabilities through logic flow manipulation, not single-line unsafe filters. Explain in great detail. Show me what lines of code you would delete and add to make this vulnerable. Make sure to not touch any other parts of the code and keep all functionalities:     
        {commit_File}
        how would you transform this commit into a vulnerable state? 

        """
        print("You: ", user_input)


        if user_input.lower() in ["exit", "quit", "stop"]:
            print("Exiting chat...")
            break
        response = chat(user_input)
        print("ChatBOT:" , response)
        #df = pd.DataFrame(response.split('\n'), columns=['Response'])
        #df = pd.DataFrame(response.splitlines(), columns=['Response'])

        with open("response.txt", "w") as f:
            f.write(response)



        assert False
        try:
            with pd.ExcelWriter(r'C:\Users\Chris\CSA-2025\chatLogger\vulTestCode.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name='NewData', index=False)
        except Exception as e:
            print("Error writing to Excel:", e)
