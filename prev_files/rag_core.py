import pymupdf, faiss, pickle
from sentence_transformers import SentenceTransformer
from pathlib import Path

def extract_pdf_chunks(pdf_path, chunk_size=500, overlap=100):
    """
    Extract text from PDF and split into overlapping chunks.
    Each chunk is ~chunk_size words with `overlap` word overlap.
    """
    doc = pymupdf.open(pdf_path) # list that splits in `n` chunks

    all_text = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        text = text.strip().replace("\n", " ")
        if text:
            all_text.append(f"[Page {page_num}]\n{text}")
    
    full_text = "\n".join(all_text)
    # print(full_text)

    # Sliding window chunking
    words = full_text.split()
    chunks = []
    for i in range(0, len(words), chunk_size-overlap):
        chunk = " ".join(words[i : i+chunk_size])
        chunks.append(chunk)
    return chunks

def create_faiss_index(chunks, model_name="BAAI/bge-large-en"):
    print(f"INFO: Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)

    print("INFO: Encodding chunks...")
    # Shape (no_of_chunks=122, 1024 (emb_dimension))
    embeddings = model.encode(chunks, convert_to_numpy=True, show_progress_bar=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    print(f"INFO: FAISS index built with {len(chunks)} chunks.")

    return index, model, embeddings

def save_index(index, chunks, model_name, path=Path(__file__).parent / "data"):
    faiss.write_index(index, str(path / "rag_index.faiss")) # Save index
    with open(path / "rag_index_chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)  # Save chunks
    with open(path / "rag_index_model_name.txt", "w") as f:
        f.write(model_name) # Save model_name -> Required later


if __name__ == "__main__":
    docs_file_path = Path(__file__).parent / "documents" / "merged2Docs.pdf"
    chunks = extract_pdf_chunks(docs_file_path)

    model_name = "BAAI/bge-large-en"
    index, model, emb = create_faiss_index(chunks, model_name)
    save_index(index, chunks, model_name)