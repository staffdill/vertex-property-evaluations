"""Integration tests for HTTP endpoints."""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """GET /api/health returns 200 with status ok."""
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_root_serves_html(client):
    """GET / returns 200 with HTML content."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


@pytest.mark.asyncio
async def test_css_accessible(client):
    """GET /css/styles.css returns 200 with CSS content."""
    resp = await client.get("/css/styles.css")
    assert resp.status_code == 200
    assert "text/css" in resp.headers["content-type"]
