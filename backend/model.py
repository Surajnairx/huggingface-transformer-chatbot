from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


# Basic greeting / casual queries
CASUAL_RESPONSES = {
    "hi": "Hello! How can I help you today?",
    "hello": "Hi there! How may I assist you?",
    "hey": "Hey! What would you like to know?",
    "good morning": "Good morning! How can I assist you today?",
    "good evening": "Good evening! What can I help you with?",
    "what is your purpose": (
        "I am here to help explain concepts, answer questions, "
        "and provide clear and detailed information."
    ),
    "who are you": (
        "I am an AI assistant designed to help answer questions "
        "and explain topics clearly."
    ),
    "how are you": "I'm doing well, thank you! How can I help you today?",
}


def check_casual_query(question):
    q = question.lower().strip()

    for key in CASUAL_RESPONSES:
        if key in q:
            return CASUAL_RESPONSES[key]

    return None


def generate_answer(answer_text, question):

    # Handle greetings / casual queries first
    casual_reply = check_casual_query(question)
    if casual_reply:
        print(f"[Casual Reply] {casual_reply}")
        return casual_reply

    prompt = (
        f"Answer the question using ONLY the information in the context below. "
        f"Do not use any outside knowledge. "
        f"If the answer is not in the context, say: I don't have information about this in the uploaded documents.\n\n"
        f"Context: {answer_text}\n\n"
        f"Question: {question}\n\n"
        f"Answer:"
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=600,
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

    # Fallback: if model returns an empty or very short unhelpful output, return context directly
    if not result or len(result) < 5:
        return answer_text

    return result