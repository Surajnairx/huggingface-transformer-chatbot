from transformers import pipeline

chatbot = pipeline(
    "text-generation",
    model="microsoft/DialoGPT-small"
)

def generate_response(user_message: str) -> str:
    result = chatbot(
        user_message,
        max_length=100,
        pad_token_id=50256
    )

    return result[0]["generated_text"]