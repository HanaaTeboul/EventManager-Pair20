from datetime import date, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (registers all tables)
from app.database import Base, get_db
from app.routers import events


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
    app.include_router(events.router)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=engine)


def make_payload(**changes):
    payload = {
        "title": "Python Workshop",
        "description": "Intro",
        "date": "2030-01-01",
        "location": "Algiers",
        "capacity": 50,
    }
    payload.update(changes)
    return payload


# ---------------- HAPPY PATH ----------------

def test_create_event_returns_201(client):
    response = client.post("/events/", json=make_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Python Workshop"
    assert body["id"] == 1


def test_get_event_by_id(client):
    created = client.post("/events/", json=make_payload()).json()
    response = client.get(f"/events/{created['id']}")
    assert response.status_code == 200
    assert response.json()["location"] == "Algiers"


def test_list_events_sorted_by_date(client):
    client.post("/events/", json=make_payload(title="Later", date="2031-01-01"))
    client.post("/events/", json=make_payload(title="Sooner", date="2030-01-01"))
    titles = [e["title"] for e in client.get("/events/").json()]
    assert titles == ["Sooner", "Later"]


def test_filter_events_by_location_case_insensitive(client):
    client.post("/events/", json=make_payload(location="Algiers"))
    client.post("/events/", json=make_payload(title="Other Event", location="Oran"))
    response = client.get("/events/", params={"location": "ALGIERS"})
    assert [e["location"] for e in response.json()] == ["Algiers"]


def test_filter_events_by_title_case_insensitive(client):
    client.post("/events/", json=make_payload(title="Python Workshop"))
    client.post("/events/", json=make_payload(title="DevOps Bootcamp"))
    response = client.get("/events/", params={"title": "python"})
    assert [e["title"] for e in response.json()] == ["Python Workshop"]


def test_update_event(client):
    created = client.post("/events/", json=make_payload()).json()
    response = client.put(
        f"/events/{created['id']}", json=make_payload(title="Updated Title")
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_delete_event(client):
    created = client.post("/events/", json=make_payload()).json()
    response = client.delete(f"/events/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/events/{created['id']}").status_code == 404


# ---------------- BOUNDARY VALUES ----------------

def test_create_event_capacity_lower_boundary(client):
    response = client.post("/events/", json=make_payload(capacity=1))
    assert response.status_code == 201


def test_create_event_capacity_upper_boundary(client):
    response = client.post("/events/", json=make_payload(capacity=10000))
    assert response.status_code == 201


def test_create_event_title_min_length_boundary(client):
    response = client.post("/events/", json=make_payload(title="abc"))
    assert response.status_code == 201


def test_create_event_today_is_allowed(client):
    response = client.post("/events/", json=make_payload(date=date.today().isoformat()))
    assert response.status_code == 201


# ---------------- NEGATIVE TESTS ----------------

def test_create_event_short_title_returns_422(client):
    response = client.post("/events/", json=make_payload(title="ab"))
    assert response.status_code == 422


@pytest.mark.parametrize("capacity", [0, -5, 10001])
def test_create_event_invalid_capacity_returns_422(client, capacity):
    response = client.post("/events/", json=make_payload(capacity=capacity))
    assert response.status_code == 422


def test_create_event_in_the_past_returns_400(client):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    response = client.post("/events/", json=make_payload(date=yesterday))
    assert response.status_code == 400
    assert response.json()["detail"] == "Event date cannot be in the past."


def test_get_missing_event_returns_404(client):
    assert client.get("/events/999").status_code == 404


def test_update_missing_event_returns_404(client):
    assert client.put("/events/999", json=make_payload()).status_code == 404


def test_update_event_to_past_date_returns_400(client):
    created = client.post("/events/", json=make_payload()).json()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    response = client.put(
        f"/events/{created['id']}", json=make_payload(date=yesterday)
    )
    assert response.status_code == 400


def test_delete_missing_event_returns_404(client):
    assert client.delete("/events/999").status_code == 404