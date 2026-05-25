from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

MODEL_NAME = "microsoft/DialoGPT-medium"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

chat_history_ids = None

def generate_response(user_message: str) -> str:
    global chat_history_ids

    new_input_ids = tokenizer.encode(
        user_message + tokenizer.eos_token,
        return_tensors="pt"
    )

    if chat_history_ids is not None:
        bot_input_ids = torch.cat(
            [chat_history_ids, new_input_ids],
            dim=-1
        )
    else:
        bot_input_ids = new_input_ids

    chat_history_ids = model.generate(
        bot_input_ids,
        max_length=1000,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        top_k=50,
        top_p=0.92,
        temperature=0.75
    )

    response = tokenizer.decode(
        chat_history_ids[:, bot_input_ids.shape[-1]:][0],
        skip_special_tokens=True
    )

    if not response.strip():
        return "I'm not sure how to respond to that."

    return response