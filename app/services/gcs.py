"""GCS service — stub for Phase 3.

Phase 3 will:
  - Install google-cloud-storage
  - Implement generate_signed_url() for direct browser-to-GCS uploads
  - Implement delete_prefix() to remove all objects under a property prefix
"""

# TODO Phase 3: from google.cloud import storage


async def delete_prefix(prefix: str) -> None:
    """Delete all GCS objects under the given prefix.

    Phase 3 implementation: list bucket objects with prefix, delete each.
    No-op in Phase 2 — no files uploaded yet.
    """
    # TODO Phase 3: implement GCS object deletion
    pass


async def generate_signed_url(gcs_uri: str, expiration_seconds: int = 900) -> str:
    """Generate a signed URL for direct browser upload.

    Phase 3 implementation: use service account credentials to sign.
    Returns empty string stub in Phase 2.
    """
    # TODO Phase 3: implement signed URL generation
    return ""
