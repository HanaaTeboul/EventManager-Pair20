"""Integration tests for the events & participants API."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def client():
    """Provide a test client with the app's lifespan (startup/shutdown) handled."""
    with TestClient(app) as test_client:
        yield test_client


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def create_event(client: TestClient, **overrides) -> dict:
    """Create an event and return the parsed response body."""
    payload = {
        "title": "Default Event",
        "location": "Constantine",
        "date": "2026-12-01",
        "capacity": 100,
    }
    payload.update(overrides)

    response = client.post("/events/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def create_participant(client: TestClient, **overrides) -> dict:
    """Create a participant and return the parsed response body."""
    payload = {
        "name": "Default Participant",
        "email": "default@example.com",
    }
    payload.update(overrides)

    response = client.post("/participants/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def test_create_and_fetch_event_integration(client: TestClient) -> None:
    """An event created via POST must be retrievable via GET by id."""
    event = create_event(
        client,
        title="DevOps Integration Conf",
        location="Constantine",
        date="2026-12-01",
        capacity=200,
    )

    get_response = client.get(f"/events/{event['id']}")

    assert get_response.status_code == 200, get_response.text
    assert get_response.json()["title"] == "DevOps Integration Conf"


def test_register_participant_to_event_integration(client: TestClient) -> None:
    """A participant registered to an event must appear in the attendees list."""
    event = create_event(
        client,
        title="Cybersecurity Workshop",
        location="NTIC",
        date="2026-11-15",
        capacity=50,
    )
    participant = create_participant(
        client,
        name="Alice Dev",
        email="alice@example.com",
    )

    register_response = client.post(
        f"/events/{event['id']}/register/{participant['id']}"
    )
    assert register_response.status_code == 200, register_response.text

    list_response = client.get(f"/events/{event['id']}/participants")
    assert list_response.status_code == 200, list_response.text
    assert any(
        attendee["id"] == participant["id"]
        for attendee in list_response.json()
    )


def test_register_non_existent_event_returns_404(client: TestClient) -> None:
    """Registering to an event that does not exist must return 404."""
    participant = create_participant(
        client,
        name="Bob Tester",
        email="bob@example.com",
    )

    response = client.post(f"/events/9999/register/{participant['id']}")

    assert response.status_code == 404