from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


def generate_answer(answer_text, question):
    prompt = f"""You are an expert professor. A student has asked you the following question.
Explain the answer below to the student in a clear, authoritative, and complete manner.
You MUST include every single key point from the answer. Do not skip or shorten any detail.

Student Question: {question}

Answer to explain: {answer_text}

Professor's complete explanation:"""

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=700,
    )

    outputs = model.generate(
        **inputs,
        max_new_tokens=300,
        num_beams=4,
        no_repeat_ngram_size=3,
        length_penalty=2.0,
        do_sample=False,
    )

    result = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    print(f"[Model] answer: {result[:150]}")
    return result
