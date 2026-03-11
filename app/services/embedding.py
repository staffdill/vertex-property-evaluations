"""Embedding service — stub for Phase 4.

Phase 4 will:
  - Install chromadb
  - Implement embed_asset() using Gemini Embedding 2 with gs:// URIs
  - Implement delete_by_property() to remove vectors from ChromaDB
"""

# TODO Phase 4: import chromadb
# TODO Phase 4: from google import generativeai


async def delete_by_property(property_id: str) -> None:
    """Delete all ChromaDB vectors associated with a property.

    Phase 4 implementation: query collection by property_id metadata, delete.
    No-op in Phase 2 — no embeddings exist yet.
    """
    # TODO Phase 4: implement ChromaDB vector deletion
    pass


async def embed_asset(asset_id: str, gcs_uri: str, file_type: str) -> None:
    """Embed an asset via Gemini Embedding 2 and store in ChromaDB.

    Phase 4 implementation: call embed_content with taskType=RETRIEVAL_DOCUMENT,
    outputDimensionality=3072, store vector with property_id metadata.
    No-op in Phase 2 stub.
    """
    # TODO Phase 4: implement Gemini embedding + ChromaDB storage
    pass
