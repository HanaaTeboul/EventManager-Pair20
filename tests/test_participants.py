import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (registers all tables)
from app.database import Base, get_db
from app.routers import participants


@pytest.fixture
def client():
    # In-memory SQLite: no events.db file, nothing touches the real database
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.include_router(participants.router)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=engine)


def make_payload(**changes):
    payload = {"name": "Sara Ben", "email": "sara@example.com"}
    payload.update(changes)
    return payload


# ---------------- HAPPY PATH ----------------

def test_create_participant_returns_201(client):
    response = client.post("/participants/", json=make_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Sara Ben"
    assert body["email"] == "sara@example.com"
    assert body["id"] == 1


def test_get_participant_by_id(client):
    created = client.post("/participants/", json=make_payload()).json()
    response = client.get(f"/participants/{created['id']}")
    assert response.status_code == 200
    assert response.json()["email"] == "sara@example.com"


def test_list_participants_sorted_by_name(client):
    client.post("/participants/", json=make_payload(name="Zed", email="z@example.com"))
    client.post("/participants/", json=make_payload(name="Adam", email="a@example.com"))
    names = [p["name"] for p in client.get("/participants/").json()]
    assert names == ["Adam", "Zed"]


def test_list_participants_empty(client):
    response = client.get("/participants/")
    assert response.status_code == 200
    assert response.json() == []


def test_delete_participant(client):
    created = client.post("/participants/", json=make_payload()).json()
    response = client.delete(f"/participants/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/participants/{created['id']}").status_code == 404


# ---------------- BOUNDARY VALUES ----------------

def test_create_participant_name_min_length_boundary(client):
    response = client.post("/participants/", json=make_payload(name="Al"))
    assert response.status_code == 201


def test_create_participant_name_max_length_boundary(client):
    response = client.post("/participants/", json=make_payload(name="A" * 100))
    assert response.status_code == 201


def test_create_participant_name_above_max_returns_422(client):
    response = client.post("/participants/", json=make_payload(name="A" * 101))
    assert response.status_code == 422


# ---------------- NEGATIVE TESTS ----------------

def test_create_participant_short_name_returns_422(client):
    response = client.post("/participants/", json=make_payload(name="A"))
    assert response.status_code == 422


def test_create_participant_invalid_email_returns_422(client):
    response = client.post("/participants/", json=make_payload(email="not-an-email"))
    assert response.status_code == 422


def test_create_participant_duplicate_email_returns_409(client):
    client.post("/participants/", json=make_payload())
    response = client.post("/participants/", json=make_payload(name="Other Person"))
    assert response.status_code == 409
    assert response.json()["detail"] == "Email is already registered."


def test_get_missing_participant_returns_404(client):
    assert client.get("/participants/999").status_code == 404


def test_delete_missing_participant_returns_404(client):
    assert client.delete("/participants/999").status_code == 404





@pytest.mark.parametrize("email", ["abc", "a@", "@b.com", "a@b", "a b@c.com", ""])
def test_create_participant_invalid_emails_return_422(client, email):
    assert client.post("/participants/", json=make_payload(email=email)).status_code == 422


def test_duplicate_email_returns_409_and_message(client):
    client.post("/participants/", json=make_payload())
    r = client.post("/participants/", json=make_payload(name="Other Person"))
    assert r.status_code == 409
    assert r.json()["detail"] == "Email is already registered."
    assert len(client.get("/participants/").json()) == 1


def test_different_email_is_not_duplicate(client):
    client.post("/participants/", json=make_payload())
    r = client.post("/participants/", json=make_payload(email="other@example.com"))
    assert r.status_code == 201


def test_get_missing_participant_message(client):
    r = client.get("/participants/999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Participant not found."


def test_delete_missing_participant_message(client):
    r = client.delete("/participants/999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Participant not found."


def test_get_participant_returns_all_fields(client):
    created = client.post("/participants/", json=make_payload()).json()
    r = client.get(f"/participants/{created['id']}")
    assert r.json() == {"id": created["id"], "name": "Sara Ben", "email": "sara@example.com"}


def test_list_participants_returns_all(client):
    client.post("/participants/", json=make_payload(name="Zed", email="z@example.com"))
    client.post("/participants/", json=make_payload(name="Adam", email="a@example.com"))
    r = client.get("/participants/")
    assert len(r.json()) == 2


def test_delete_participant_has_empty_body(client):
    created = client.post("/participants/", json=make_payload()).json()
    r = client.delete(f"/participants/{created['id']}")
    assert r.status_code == 204
    assert r.content == b""