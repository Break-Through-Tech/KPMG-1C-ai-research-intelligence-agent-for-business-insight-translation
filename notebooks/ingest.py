"""
Ingestion for the research RAG pipeline: parsed papers -> chunks -> Chroma.

Packages the Document preparation, chunking and storage cells of
`eda_workbook.ipynb` so the full dataset can be (re)built in one call:

- ingests every parsed paper, not the 5-paper sample
- uses cosine distance, so relevance scores are real similarities in [0, 1]
- stores full paper metadata (authors, date, categories, collection areas)
  on every chunk for citations and filtering

Usage from `notebooks/` after the parsing cell (`parsed_pdfs_dict`, `unique_papers`):

    from ingest import build_vector_store
    vector_store = build_vector_store(parsed_pdfs_dict, unique_papers, embeddings)
"""

from langchain_core.documents import Document

DEFAULT_PERSIST_DIRECTORY = "arxiv_data/chroma_db"
DEFAULT_COLLECTION_NAME = "research_mpnet_cosine_v2"
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"


def join_list(values) -> str:
    """Chroma metadata only holds scalars, so lists are stored as 'a, b, c'."""
    return ", ".join(values or [])


def build_documents(parsed_pdfs: dict, papers: list[dict]) -> list[Document]:
    """One Document per non-empty section, keyed to its paper's metadata.

    `parsed_pdfs` maps title -> {heading: text, "all": text}, as produced by
    the parsing cell. `papers` is the metadata list (`unique_papers`).
    """
    metadata_by_title = {}
    for paper in papers:
        if paper["title"] in metadata_by_title:
            raise ValueError(f"Duplicate title found: {paper['title']}")
        metadata_by_title[paper["title"]] = paper

    documents = []
    for title, sections in parsed_pdfs.items():
        paper = metadata_by_title.get(title)
        if paper is None:
            raise ValueError(f"No metadata found for paper: {title}")

        headings = [heading for heading in sections if heading != "all"]
        for section_order, heading in enumerate(headings):
            text = sections[heading].strip()
            if not text:
                continue
            documents.append(Document(page_content=text, metadata={
                "title": title,
                "section": heading,
                "section_order": section_order,
                "paper_id": paper["id"],
                "source_url": paper.get("source_url", ""),
                "authors": join_list(paper.get("authors")),
                "published": (paper.get("published") or "")[:10],
                "primary_category": paper.get("primary_category") or "",
                "categories": join_list(paper.get("categories")),
                "collection_areas": join_list(paper.get("collection_areas")),
            }))
    return documents


def mpnet_token_counter():
    """Token counter matching the embedding model, as in the notebook."""
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)
    return lambda text: len(tokenizer(text, add_special_tokens=False)["input_ids"])


def chunk_documents(documents, chunk_size=350, chunk_overlap=50, length_function=None):
    """Split section Documents into chunks (sizes in mpnet tokens by default)."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=length_function or mpnet_token_counter(),
    )
    chunks = [chunk for chunk in splitter.split_documents(documents) if chunk.page_content.strip()]

    missing = {doc.metadata["paper_id"] for doc in documents} - {c.metadata["paper_id"] for c in chunks}
    if missing:
        raise ValueError(f"Papers missing from chunks: {sorted(missing)}")
    return chunks


def chunk_ids(chunks) -> list[str]:
    """Stable ids '<paper_id>_<section_order>_<n>' so re-ingesting overwrites, not duplicates."""
    counts = {}
    ids = []
    for chunk in chunks:
        key = (chunk.metadata["paper_id"], chunk.metadata["section_order"])
        counts[key] = counts.get(key, 0) + 1
        ids.append(f"{key[0]}_{key[1]}_{counts[key]}")
    return ids


def build_vector_store(
    parsed_pdfs: dict,
    papers: list[dict],
    embeddings,
    persist_directory=DEFAULT_PERSIST_DIRECTORY,
    collection_name=DEFAULT_COLLECTION_NAME,
    length_function=None,
    batch_size=200,
    resume=True,
):
    """Build (or refresh) the cosine Chroma collection from parsed papers.

    Prints progress after every batch. With `resume=True`, chunks already in
    the collection (e.g. from an interrupted run) are skipped, not re-embedded.
    """
    import time
    from langchain_chroma import Chroma

    started = time.time()
    chunks = chunk_documents(build_documents(parsed_pdfs, papers), length_function=length_function)
    ids = chunk_ids(chunks)
    print(f"Chunked {len(chunks)} chunks in {(time.time() - started) / 60:.1f} min.", flush=True)

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(persist_directory),
        collection_metadata={"hnsw:space": "cosine"},
    )

    pending = list(zip(chunks, ids))
    if resume:
        stored = set(vector_store.get(ids=ids, include=[])["ids"])
        pending = [(chunk, chunk_id) for chunk, chunk_id in pending if chunk_id not in stored]
        if stored:
            print(f"Resuming: {len(stored)} chunks already stored, {len(pending)} to embed.", flush=True)

    embed_started = time.time()
    for start in range(0, len(pending), batch_size):
        batch = pending[start:start + batch_size]
        vector_store.add_documents([chunk for chunk, _ in batch], ids=[chunk_id for _, chunk_id in batch])
        done = start + len(batch)
        print(f"  embedded {done}/{len(pending)} chunks ({done / len(pending):.0%}) "
              f"- {(time.time() - embed_started) / 60:.1f} min", flush=True)

    print(f"Stored {len(chunks)} chunks from {len({c.metadata['paper_id'] for c in chunks})} papers "
          f"in '{collection_name}'.")
    return vector_store
