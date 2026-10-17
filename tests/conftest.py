from datetime import date

import pytest


# 1. Valid event data
@pytest.fixture
def sample_event_dict():
    return {
        "title": "Python Workshop",
        "description": "Intro",
        "date": date(2030, 1, 1),
        "location": "Algiers",
        "capacity": 50,
    }


# 2. Valid participant data
@pytest.fixture
def sample_participant_dict():
    return {
        "name": "Sara Ben",
        "email": "sara@example.com",
    }


# 3. Empty in-memory store, cleared after each test
@pytest.fixture
def mock_event_store():
    store = []
    yield store          # the test runs here
    store.clear()        # teardown


# 4. Store pre-filled with 3 events (uses fixture #3)
@pytest.fixture
def prepopulated_event_store(mock_event_store):
    mock_event_store.append({
        "title": "Python Workshop",
        "description": "Intro",
        "date": date(2030, 1, 1),
        "location": "Algiers",
        "capacity": 50,
    })
    mock_event_store.append({
        "title": "Cyber Security Talk",
        "description": "Basics",
        "date": date(2030, 2, 1),
        "location": "Blida",
        "capacity": 100,
    })
    mock_event_store.append({
        "title": "DevOps Bootcamp",
        "description": "CI/CD",
        "date": date(2030, 3, 1),
        "location": "Oran",
        "capacity": 30,
    })
    return mock_event_store


# 5. Runs automatically around every test
@pytest.fixture(autouse=True)
def global_environment_logger():
    print("\n[SETUP] test starting")
    yield
    print("[TEARDOWN] test finished")