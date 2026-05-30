from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

CASUAL_RESPONSES = {
    "hi": "Hello! How can I help you today?",
    "hello": "Hi there! How may I assist you?",
    "hey": "Hey! What would you like to know?",
    "good morning": "Good morning! How can I assist you today?",
    "good evening": "Good evening! What can I help you with?",
    "how are you": "I'm doing well, thank you! How can I help you today?",
    "who are you": (
        "I am an AI assistant designed to answer questions "
        "based on uploaded PDF documents."
    ),
    "what is your purpose": (
        "My purpose is to help users understand uploaded PDF documents "
        "by answering questions using the document content."
    ),
}


def check_casual_query(question):
    q = question.lower().strip()

    for key, response in CASUAL_RESPONSES.items():
        if q == key:
            return response

    return None


def generate_answer(context, question):
    casual_reply = check_casual_query(question)

    if casual_reply:
        print(f"[Casual Reply] {casual_reply}")
        return casual_reply

    prompt = f"""
You are a helpful AI document assistant.

Answer the question using ONLY the context provided below.
Do not use outside knowledge.

If the answer is not found in the context, say:
I don't have information about this in the uploaded documents.

Context:
{context}

Question:
{question}

Answer:
"""

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=900,
    )

    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        num_beams=4,
        no_repeat_ngram_size=3,
        length_penalty=1.5,
        do_sample=False,
    )

    result = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    print(f"[Model] answer: {result[:150]}")

    if not result or len(result) < 5:
        return "I don't have information about this in the uploaded documents."

    return result