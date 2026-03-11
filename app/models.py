"""Pydantic request and response models."""

from typing import Optional

from pydantic import BaseModel, Field


class PropertyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    address: str = Field(..., min_length=1, max_length=500)


class PropertyResponse(BaseModel):
    id: str
    name: str
    address: str
    created_at: str
    asset_count: int = 0
    risk_badge: Optional[str] = None  # null until Phase 5 analysis


class AssetResponse(BaseModel):
    id: str
    property_id: str
    filename: Optional[str] = None
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    gcs_uri: Optional[str] = None
    embedded: int = 0
    created_at: str
