from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_name = "facebook/opt-6.7b"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name
)

prompt = "write cooking recipes of hamburger"

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(
    **inputs,
    max_new_tokens=150,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
    repetition_penalty=1.2,
    no_repeat_ngram_size=3,
)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
