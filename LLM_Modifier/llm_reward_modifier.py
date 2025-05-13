# LLM_Modifier/llm_reward_modifier.py

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os


class LLMRewardEnhancer:
    def __init__(self, model_id=None, local_path=True):
        model_id ="meta-llama/Meta-Llama-3.1-8B-Instruct"

        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )

    def generate_reward_function_suggestion(self, prompt: str) -> str:
        formatted_prompt = f"<s>[INST] {prompt.strip()} [/INST]"
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=True,
                temperature=0.7,
                top_p=0.95
            )

        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return decoded.replace(formatted_prompt, "").strip()