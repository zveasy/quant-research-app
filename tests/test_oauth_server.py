import os
import sys
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx
from httpx import ASGITransport
import pytest
from sqlmodel import SQLModel, Session, select


@pytest.mark.asyncio
async def test_oauth_flow(tmp_path, monkeypatch):
    db_path = tmp_path / "db.sqlite"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("OAUTH_SECRET_KEY", "test-secret")

    from oauth_server import app, engine

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/register_tenant", json={"tenant_name": "foo"})
        assert resp.status_code == 200
        creds = resp.json()
        client_id = creds["client_id"]
        client_secret = creds["client_secret"]

        from oauth_server import Tenant
        with Session(engine) as s:
            tenant = s.exec(select(Tenant).where(Tenant.client_id == client_id)).first()
            assert tenant is not None
            assert tenant.hashed_secret != client_secret

        redirect_uri = "http://localhost/cb"
        resp = await client.get("/authorize", params={"client_id": client_id, "redirect_uri": redirect_uri})
        assert resp.status_code in (302, 307)
        loc = resp.headers["location"]
        qs = parse_qs(urlparse(loc).query)
        code = qs["code"][0]

        resp = await client.post(
            "/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": client_id,
                "client_secret": client_secret,
            },
        )
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        assert token
