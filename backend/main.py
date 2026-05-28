from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import re

from rag import extract_text_from_pdf, create_vector_store, search_similar_chunks, list_indexed_pdfs
from model import generate_answer

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
            "answer": "No relevant information found in the uploaded documents.",
            "similarity_scores": [],
            "sources": [],
        }

    answer_text = extract_answer_text(results[0]["chunk"])
    answer = generate_answer(answer_text, question)

    return {
        "answer": answer,
        "similarity_scores": [r["similarity"] for r in results],
        "sources": [r["pdf_name"] for r in results],
    }
