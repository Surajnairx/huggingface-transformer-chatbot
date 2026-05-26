from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

chunks = []
index = None


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def split_text(text, chunk_size=500, overlap=100):
    result = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        result.append(text[start:end])
        start += chunk_size - overlap

    return result


def create_vector_store(text):
    global chunks, index

    chunks = split_text(text)

    embeddings = embedding_model.encode(chunks)
    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    return len(chunks)


def search_similar_chunks(question, top_k=2):
    global chunks, index

    if index is None:
        return []

    question_embedding = embedding_model.encode([question])
    question_embedding = np.array(question_embedding).astype("float32")

    distances, indices = index.search(question_embedding, top_k)

    results = []
    for i in indices[0]:
        if i < len(chunks):
            results.append(chunks[i])

    return results