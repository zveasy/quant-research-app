from __future__ import annotations

import hashlib
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from authlib.jose import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./oauth.db")
SECRET_KEY = os.getenv("OAUTH_SECRET_KEY", "change-me")

engine = create_engine(DATABASE_URL)


class Tenant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_name: str
    client_id: str = Field(index=True, unique=True)
    hashed_secret: str


class AuthorizationCode(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True)
    client_id: str
    redirect_uri: str
    expires_at: datetime


class Token(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    access_token: str = Field(index=True, unique=True)
    client_id: str
    expires_at: datetime


class TenantCreate(BaseModel):
    tenant_name: str


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()

SQLModel.metadata.create_all(engine)


@app.post("/register_tenant")
async def register_tenant(data: TenantCreate, session: Session = Depends(get_session)):
    client_id = secrets.token_urlsafe(16)
    client_secret = secrets.token_urlsafe(32)
    hashed = hashlib.sha256(client_secret.encode()).hexdigest()
    tenant = Tenant(tenant_name=data.tenant_name, client_id=client_id, hashed_secret=hashed)
    session.add(tenant)
    session.commit()
    return {"client_id": client_id, "client_secret": client_secret}


@app.get("/authorize")
async def authorize(request: Request, client_id: str, redirect_uri: str, state: Optional[str] = None, session: Session = Depends(get_session)):
    tenant = session.exec(select(Tenant).where(Tenant.client_id == client_id)).first()
    if not tenant:
        raise HTTPException(status_code=400, detail="invalid_client")
    code = secrets.token_urlsafe(16)
    exp = datetime.utcnow() + timedelta(minutes=5)
    auth_code = AuthorizationCode(code=code, client_id=client_id, redirect_uri=redirect_uri, expires_at=exp)
    session.add(auth_code)
    session.commit()
    location = f"{redirect_uri}?code={code}"
    if state:
        location += f"&state={state}"
    return RedirectResponse(url=location)


@app.post("/token")
async def token(
    grant_type: str = Form("authorization_code"),
    code: str = Form(...),
    redirect_uri: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    session: Session = Depends(get_session),
):
    if grant_type != "authorization_code":
        raise HTTPException(status_code=400, detail="unsupported_grant_type")
    auth_code = session.exec(select(AuthorizationCode).where(AuthorizationCode.code == code)).first()
    if not auth_code or auth_code.expires_at < datetime.utcnow() or auth_code.client_id != client_id or auth_code.redirect_uri != redirect_uri:
        raise HTTPException(status_code=400, detail="invalid_grant")
    tenant = session.exec(select(Tenant).where(Tenant.client_id == client_id)).first()
    if not tenant or hashlib.sha256(client_secret.encode()).hexdigest() != tenant.hashed_secret:
        raise HTTPException(status_code=401, detail="invalid_client")
    access_payload = {"client_id": client_id, "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp())}
    access_token = jwt.encode({"alg": "HS256"}, access_payload, SECRET_KEY).decode()
    token = Token(access_token=access_token, client_id=client_id, expires_at=datetime.utcnow() + timedelta(hours=1))
    session.add(token)
    session.delete(auth_code)
    session.commit()
    return {"access_token": access_token, "token_type": "bearer"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
