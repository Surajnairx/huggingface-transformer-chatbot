from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
import re

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
SIMILARITY_THRESHOLD = 0.4
CHROMA_PATH = "./chroma_db"
TOP_K = 3

embedding_model = SentenceTransformer(EMBEDDING_MODEL)

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(
    name="pdf_chunks",
    metadata={"hnsw:space": "cosine"},
)


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def split_text(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    chunks = []
    current = []

    for line in lines:
        if re.match(r'^Q\d*[\.:]?\s', line, re.IGNORECASE):
            if current:
                chunks.append("\n".join(current))
            current = [line]
        else:
            current.append(line)

    if current:
        chunks.append("\n".join(current))

    return [c for c in chunks if c.strip()]


def create_vector_store(text, pdf_name):
    chunks = split_text(text)
    print(f"[VectorDB] Split into {len(chunks)} Q&A chunks")

    embeddings = embedding_model.encode(
        chunks, normalize_embeddings=True, show_progress_bar=False
    ).tolist()

    existing = collection.get(where={"pdf_name": pdf_name})
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    ids = [f"{pdf_name}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"pdf_name": pdf_name, "chunk_index": i} for i in range(len(chunks))]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )

    print(f"[VectorDB] Stored {len(chunks)} chunks for '{pdf_name}'")
    return len(chunks)


def search_similar_chunks(question, top_k=TOP_K):
    total = collection.count()
    if total == 0:
        return []

    prefixed_query = f"Represent this sentence for searching relevant passages: {question}"
    query_embedding = embedding_model.encode(
        [prefixed_query], normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, total),
        include=["documents", "distances", "metadatas"],
    )

    chunks = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    output = []
    print("\n--- Retrieval Results ---")
    for chunk, dist, meta in zip(chunks, distances, metadatas):
        similarity = round(1.0 - dist, 4)
        print(f"  PDF: {meta['pdf_name']} | chunk {meta['chunk_index']} | cosine similarity: {similarity:.4f}")
        if similarity >= SIMILARITY_THRESHOLD:
            output.append({"chunk": chunk, "similarity": similarity, "pdf_name": meta["pdf_name"]})

    print(f"  Kept {len(output)}/{len(chunks)} chunks above threshold {SIMILARITY_THRESHOLD}")
    print("-------------------------\n")

    return output


def list_indexed_pdfs():
    all_meta = collection.get(include=["metadatas"])["metadatas"]
    return list({m["pdf_name"] for m in all_meta})
