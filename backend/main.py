from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import re
import random

from rag import extract_text_from_pdf, create_vector_store, search_similar_chunks, list_indexed_pdfs
from model import generate_answer

GREETINGS = {
    "greet": {
        "patterns": [
            r"^(hi|hello|hey|howdy|hiya|sup|what'?s up|greetings|good\s*(morning|afternoon|evening|day))[!?.,]?$"
        ],
        "responses": [
            "Hello! How can I help you today? You can upload a PDF and ask me questions about it.",
            "Hey there! Ready to help. Upload a PDF document and I'll answer your questions about it.",
            "Hi! I'm your PDF assistant. Upload a document and ask away!",
        ],
    },
    "how_are_you": {
        "patterns": [
            r"how (are you|is it going|do you do|have you been|r u)[?!.,]?$",
            r"how'?s (it going|everything|life|things)[?!.,]?$",
            r"(what'?s up|wassup|how goes it)[?!.,]?$",
        ],
        "responses": [
            "I'm doing great, thanks for asking! Ready to help you explore your PDF documents.",
            "All good here! I'm here to answer questions about any PDF you upload.",
            "Doing well! Let me know what document you'd like to dive into.",
        ],
    },
    "capabilities": {
        "patterns": [
            r"what (can you do|are you capable of|do you do|are your capabilities|can you help with)[?!.,]?$",
            r"(what'?s your purpose|how do you work|tell me about yourself|who are you|what are you)[?!.,]?$",
            r"help$",
            r"(show me|list) (your )?(features|capabilities|functions)[?!.,]?$",
        ],
        "responses": [
            (
                "I'm a PDF Q&A assistant! Here's what I can do:\n\n"
                "📄 **Upload PDFs** — Send me any PDF document to index.\n"
                "❓ **Answer Questions** — Ask anything about the content of your uploaded PDFs.\n"
                "📚 **Multi-document** — I can handle multiple PDFs at once and tell you which one the answer came from.\n\n"
                "Just upload a PDF and start asking questions!"
            ),
        ],
    },
    "thanks": {
        "patterns": [
            r"^(thanks|thank you|thank u|thx|ty|cheers)[!.,]?$",
            r"^(thanks|thank you) (so much|a lot|very much)[!.,]?$",
        ],
        "responses": [
            "You're welcome! Feel free to ask more questions.",
            "Happy to help! Let me know if you have more questions.",
            "Anytime! Ask me anything about your documents.",
        ],
    },
    "goodbye": {
        "patterns": [
            r"^(bye|goodbye|see you|see ya|later|cya|good night|good bye)[!.,]?$",
        ],
        "responses": [
            "Goodbye! Come back anytime you have documents to explore.",
            "See you later! Happy to help whenever you need.",
            "Bye! Feel free to return with more questions.",
        ],
    },
}


def get_casual_response(text: str):
    normalized = text.strip().lower()
    for category, data in GREETINGS.items():
        for pattern in data["patterns"]:
            if re.search(pattern, normalized):
                return random.choice(data["responses"])
    return None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def extract_answer_text(chunk):
    lines = chunk.strip().split("\n")
    answer_lines = []
    past_question = False
    for line in lines:
        if not past_question and re.match(r'^Q\d*[\.:]?\s', line, re.IGNORECASE):
            past_question = True
            continue
        if line.strip():
            answer_lines.append(line.strip())
    return " ".join(answer_lines) if answer_lines else chunk


@app.get("/")
def home():
    return {"message": "AI-Powered PDF Question Answering Backend is running"}


@app.get("/list-pdfs")
def list_pdfs():
    return {"pdfs": list_indexed_pdfs()}


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    text = extract_text_from_pdf(file_path)
    total_chunks = create_vector_store(text, pdf_name=file.filename)
    return {
        "message": f"'{file.filename}' uploaded and indexed successfully",
        "chunks": total_chunks,
    }


@app.post("/ask-document")
async def ask_document(data: dict):
    question = data.get("question")
    results = search_similar_chunks(question)

    if not results:
        return {
            "answer": "I couldn't find relevant information about this in the uploaded documents. Please try rephrasing or ask something covered in the document.",
            "similarity_scores": [],
            "sources": [],
        }

    top_score = results[0]["similarity"]
    if top_score < 0.5:
        return {
            "answer": "Your question doesn't seem to be covered in the uploaded documents. Please ask something related to the document content.",
            "similarity_scores": [r["similarity"] for r in results],
            "sources": [],
        }

    answer_text = extract_answer_text(results[0]["chunk"])
    answer = generate_answer(answer_text, question)

    return {
        "answer": answer,
        "similarity_scores": [r["similarity"] for r in results],
        "sources": [r["pdf_name"] for r in results],
    }
