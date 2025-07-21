from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, TaskType
import os
import json
from config_loader import ConfigLoader

class JavaTrainerAI(): 
    def __init__(self):
        cfg = ConfigLoader("Credentials.json")
        HUGGINGFACE_HUB_TOKEN = cfg.HUGGINGFACE_HUB_TOKEN
        self.ds = load_dataset("semeru/code-text-java", split = "train")  
        self.model_id = "codellama/CodeLlama-34b-instruct"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, trust_remote_code=True, token=HUGGINGFACE_HUB_TOKEN)
        self.base = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            trust_remote_code=True,
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            device_map="auto",           # auto-assign layers across all available GPUs
        )
        self.base.gradient_checkpointing_enable()


    def loraAdapter(self): 
        self.lora_cfg = LoraConfig(
        task_type=TaskType.CAUSAL_LM,  r=8, lora_alpha=16, lora_dropout=0.1,
        target_modules=["q_proj","v_proj"])
        self.model = get_peft_model(self.base, self.lora_cfg)

    def chunk(self, ex): 
        return self.tokenizer(
            ex["original_string"],
            truncation=True, max_length=512, stride=64,
            return_overflowing_tokens=True,
            )
    def TrainRun(self, output_dir = "codellama_java_adapt", epochs=1, batch_size = 1): 
        if not hasattr(self, "model"):
            self.loraAdapter()
        lm_ds = self.ds.map(self.chunk, batched=True, remove_columns=self.ds.column_names)
        data_collator = DataCollatorForLanguageModeling(self.tokenizer, mlm=False)
        args = TrainingArguments(
            output_dir="codellama_java_adapt",
            per_device_train_batch_size=1,
            gradient_accumulation_steps=8,
            fp16=True,
            logging_steps=300,
            save_total_limit=1,
            ddp_find_unused_parameters=False
        )
        trainer = Trainer(
            model=self.model, args=args,
            train_dataset=lm_ds,
            data_collator=DataCollatorForLanguageModeling(self.tokenizer, mlm=False),
            tokenizer=self.tokenizer,
        )
        trainer.train()
        self.model.save_pretrained("codellama_java_adapt")
        self.tokenizer.save_pretrained("codellama_java_adapt")
        os.makedirs(output_dir, exist_ok=True)
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
    
if __name__ == "__main__":
    trainer = JavaTrainerAI()
    trainer.loraAdapter()            
    trainer.TrainRun(epochs=1) 
