from app.event_filter import (
    filter_events_by_location,
    filter_events_by_title,
)


def test_filter_events_by_location(prepopulated_event_store):
    result = filter_events_by_location(
        prepopulated_event_store,
        "BLIDA",
    )

    assert len(result) == 1
    assert result[0]["location"] == "Blida"


def test_filter_events_by_title(prepopulated_event_store):
    result = filter_events_by_title(
        prepopulated_event_store,
        "SECURITY",
    )

    assert len(result) == 1
    assert result[0]["title"] == "Cyber Security Talk"


def test_filter_location_with_partial_match(prepopulated_event_store):
    result = filter_events_by_location(
        prepopulated_event_store,
        "oran",
    )

    assert len(result) == 1
    assert result[0]["title"] == "DevOps Bootcamp"


def test_filter_title_with_partial_match(prepopulated_event_store):
    result = filter_events_by_title(
        prepopulated_event_store,
        "python",
    )

    assert len(result) == 1
    assert result[0]["title"] == "Python Workshop"

