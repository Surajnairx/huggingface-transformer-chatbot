from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from rag import (
    extract_text_from_pdf,
    create_vector_store,
    search_similar_chunks,
)

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


@app.get("/")
def home():
    return {
        "message": "AI-Powered PDF Question Answering Backend is running"
    }


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text_from_pdf(file_path)

    total_chunks = create_vector_store(text)

    return {
        "message": "PDF uploaded and processed successfully",
        "chunks": total_chunks,
    }


@app.post("/ask-document")
async def ask_document(data: dict):

    question = data.get("question")

    relevant_chunks = search_similar_chunks(question)

    if not relevant_chunks:
        return {
            "answer": "No relevant information found in the document.",
            "context": [],
        }

    context = "\n".join(relevant_chunks)

    answer = generate_answer(context, question)

    return {
        "answer": answer,
        "context": relevant_chunks,
    }