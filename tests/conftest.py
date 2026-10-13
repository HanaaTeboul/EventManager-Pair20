import pytest
from app.schemas import Event


@pytest.fixture
def sample_event_dict():
    return {"title": "PyCon Algeria", "location": "Constantine", "capacity": 100}


@pytest.fixture
def sample_participant_dict():
    return {"name": "Amine", "email": "amine@example.com"}


@pytest.fixture
def mock_event_store():
    store = []          # in-memory repository
    yield store
    store.clear()       # teardown


@pytest.fixture
def prepopulated_event_store(mock_event_store):
    mock_event_store.extend([
        Event(title="Python Workshop", location="Constantine", capacity=50),
        Event(title="Cyber Security Summit", location="Algiers", capacity=500),
        Event(title="DevOps Day", location="Oran", capacity=200),
    ])
    return mock_event_store


@pytest.fixture(autouse=True)
def global_environment_logger():
    print("\n[SETUP] test starting")
    yield
    print("[TEARDOWN] test finished")
