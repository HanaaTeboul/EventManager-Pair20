import pytest
from pydantic import ValidationError

from app.event_filter import (
    filter_events_by_location,
    filter_events_by_title,
)
from app.schemas import EventCreate


# ---------------- FILTER TESTS (already written) ----------------

def test_filter_events_by_location(prepopulated_event_store):
    result = filter_events_by_location(prepopulated_event_store, "BLIDA")
    assert len(result) == 1
    assert result[0]["location"] == "Blida"


def test_filter_events_by_title(prepopulated_event_store):
    result = filter_events_by_title(prepopulated_event_store, "SECURITY")
    assert len(result) == 1
    assert result[0]["title"] == "Cyber Security Talk"


def test_filter_location_with_partial_match(prepopulated_event_store):
    result = filter_events_by_location(prepopulated_event_store, "oran")
    assert len(result) == 1
    assert result[0]["title"] == "DevOps Bootcamp"


def test_filter_title_with_partial_match(prepopulated_event_store):
    result = filter_events_by_title(prepopulated_event_store, "python")
    assert len(result) == 1
    assert result[0]["title"] == "Python Workshop"


# ---------------- HAPPY PATH ----------------

def test_valid_event_creation(sample_event_dict):
    event = EventCreate(**sample_event_dict)
    assert event.title == "Python Workshop"
    assert event.capacity == 50


# ---------------- BOUNDARY VALUES ----------------

def test_capacity_lower_boundary(sample_event_dict):
    sample_event_dict["capacity"] = 1
    assert EventCreate(**sample_event_dict).capacity == 1


def test_capacity_upper_boundary(sample_event_dict):
    sample_event_dict["capacity"] = 10000
    assert EventCreate(**sample_event_dict).capacity == 10000


def test_title_min_length_boundary(sample_event_dict):
    sample_event_dict["title"] = "abc"
    assert EventCreate(**sample_event_dict).title == "abc"


# ---------------- NEGATIVE TESTS ----------------

def test_short_title_raises(sample_event_dict):
    sample_event_dict["title"] = "ab"
    with pytest.raises(ValidationError):
        EventCreate(**sample_event_dict)


def test_capacity_zero_raises(sample_event_dict):
    sample_event_dict["capacity"] = 0
    with pytest.raises(ValidationError):
        EventCreate(**sample_event_dict)


def test_capacity_negative_raises(sample_event_dict):
    sample_event_dict["capacity"] = -5
    with pytest.raises(ValidationError):
        EventCreate(**sample_event_dict)


def test_capacity_above_max_raises(sample_event_dict):
    sample_event_dict["capacity"] = 10001
    with pytest.raises(ValidationError):
        EventCreate(**sample_event_dict)