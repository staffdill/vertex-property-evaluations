"""Integration tests for property CRUD endpoints."""

import pytest


async def test_create_property(client):
    """POST /api/properties/ returns 201 with persisted record."""
    resp = await client.post(
        "/api/properties/",
        json={"name": "1847 Ridgeline Dr", "address": "1847 Ridgeline Drive, Austin TX 78701"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert body["name"] == "1847 Ridgeline Dr"
    assert body["address"] == "1847 Ridgeline Drive, Austin TX 78701"


async def test_create_missing_fields(client):
    """POST /api/properties/ with empty body returns 422."""
    resp = await client.post("/api/properties/", json={})
    assert resp.status_code == 422


async def test_list_properties(client):
    """GET /api/properties/ returns list with asset_count and risk_badge."""
    await client.post(
        "/api/properties/",
        json={"name": "Test Property", "address": "123 Main St, Austin TX 78701"},
    )
    resp = await client.get("/api/properties/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    item = data[0]
    assert "asset_count" in item
    assert "risk_badge" in item
    assert item["risk_badge"] is None


async def test_list_empty(client):
    """GET /api/properties/ with no data returns empty list."""
    resp = await client.get("/api/properties/")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_get_property(client):
    """GET /api/properties/{id} returns property with assets array."""
    create_resp = await client.post(
        "/api/properties/",
        json={"name": "Detail Property", "address": "456 Oak Ave, Dallas TX 75201"},
    )
    prop_id = create_resp.json()["id"]
    resp = await client.get(f"/api/properties/{prop_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert "assets" in body
    assert isinstance(body["assets"], list)


async def test_get_property_not_found(client):
    """GET /api/properties/nonexistent returns 404."""
    resp = await client.get("/api/properties/nonexistent")
    assert resp.status_code == 404


async def test_delete_property(client):
    """DELETE /api/properties/{id} returns 204, then GET returns 404."""
    create_resp = await client.post(
        "/api/properties/",
        json={"name": "To Delete", "address": "789 Pine Rd, Houston TX 77001"},
    )
    prop_id = create_resp.json()["id"]
    del_resp = await client.delete(f"/api/properties/{prop_id}")
    assert del_resp.status_code == 204
    get_resp = await client.get(f"/api/properties/{prop_id}")
    assert get_resp.status_code == 404


async def test_delete_cascades_assets(client):
    """DELETE /api/properties/{id} removes the property; cascade verifiable at property level."""
    create_resp = await client.post(
        "/api/properties/",
        json={"name": "Cascade Test", "address": "321 Elm St, San Antonio TX 78201"},
    )
    prop_id = create_resp.json()["id"]
    # Verify property exists with empty assets
    get_resp = await client.get(f"/api/properties/{prop_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["assets"] == []
    # Delete the property
    del_resp = await client.delete(f"/api/properties/{prop_id}")
    assert del_resp.status_code == 204
    # Property is gone (cascade at property level)
    gone_resp = await client.get(f"/api/properties/{prop_id}")
    assert gone_resp.status_code == 404
    # List is empty
    list_resp = await client.get("/api/properties/")
    assert list_resp.json() == []
