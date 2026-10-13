import pytest
from pydantic import ValidationError
from app.schemas import Event
from app.services import filter_events_by_location, filter_events_by_title


# ---------- Happy path ----------
def test_valid_event_creation(sample_event_dict):
    event = Event(**sample_event_dict)
    assert event.title == "PyCon Algeria"
    assert event.capacity == 100


def test_filter_by_location_case_insensitive(prepopulated_event_store):
    result = filter_events_by_location(prepopulated_event_store, "cONSTANTINE")
    assert len(result) == 1
    assert result[0].title == "Python Workshop"


def test_filter_by_title_case_insensitive(prepopulated_event_store):
    result = filter_events_by_title(prepopulated_event_store, "devops")
    assert [e.location for e in result] == ["Oran"]


def test_filter_no_match_returns_empty(prepopulated_event_store):
    assert filter_events_by_title(prepopulated_event_store, "zzz") == []


# ---------- Boundary values ----------
def test_capacity_minimum_boundary(sample_event_dict):
    sample_event_dict["capacity"] = 1
    assert Event(**sample_event_dict).capacity == 1


def test_capacity_maximum_boundary(sample_event_dict):
    sample_event_dict["capacity"] = 10_000
    assert Event(**sample_event_dict).capacity == 10_000


def test_title_length_exactly_three(sample_event_dict):
    sample_event_dict["title"] = "abc"
    assert len(Event(**sample_event_dict).title) == 3


# ---------- Negative ----------
def test_short_title_rejected(sample_event_dict):
    sample_event_dict["title"] = "ab"
    with pytest.raises(ValidationError):
        Event(**sample_event_dict)


@pytest.mark.parametrize("bad_capacity", [0, -5, 10_001])
def test_invalid_capacity_rejected(sample_event_dict, bad_capacity):
    sample_event_dict["capacity"] = bad_capacity
    with pytest.raises(ValidationError):
        Event(**sample_event_dict)
