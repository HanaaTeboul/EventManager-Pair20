import pytest
from pydantic import ValidationError

from app.schemas import ParticipantCreate
from app.services.registration_rules import (
    has_available_capacity,
    check_duplicate_registration,
)


# ---------------------------------------------------------
# HAPPY PATH TESTS (valid input, expected success)
# ---------------------------------------------------------

def test_valid_participant_creation(sample_participant_dict):
    participant = ParticipantCreate(**sample_participant_dict)
    assert participant.name == "Sara Ben"
    assert participant.email == "sara@example.com"


def test_has_available_capacity_true():
    assert has_available_capacity(5, 10) is True


def test_no_duplicate_does_not_raise():
    # new id is not in the list, so nothing should happen
    check_duplicate_registration([1, 2, 3], 4)


# ---------------------------------------------------------
# BOUNDARY VALUE TESTS (exact limits)
# ---------------------------------------------------------

def test_capacity_one_below_max():
    # current = max - 1  -> still room
    assert has_available_capacity(9, 10) is True


def test_capacity_equal_to_max():
    # current = max  -> full
    assert has_available_capacity(10, 10) is False


def test_capacity_above_max():
    # current > max  -> over capacity
    assert has_available_capacity(11, 10) is False


def test_name_min_length_boundary(sample_participant_dict):
    # name of exactly 2 characters is valid
    sample_participant_dict["name"] = "Al"
    participant = ParticipantCreate(**sample_participant_dict)
    assert participant.name == "Al"


def test_capacity_zero_current_count():
    # empty event still has room
    assert has_available_capacity(0, 1) is True


# ---------------------------------------------------------
# NEGATIVE TESTS (invalid input, expected errors)
# ---------------------------------------------------------

def test_invalid_email_raises(sample_participant_dict):
    sample_participant_dict["email"] = "not-an-email"
    with pytest.raises(ValidationError):
        ParticipantCreate(**sample_participant_dict)


def test_short_name_raises(sample_participant_dict):
    # 1 character is below the minimum of 2
    sample_participant_dict["name"] = "A"
    with pytest.raises(ValidationError):
        ParticipantCreate(**sample_participant_dict)


def test_duplicate_registration_raises():
    with pytest.raises(ValueError):
        check_duplicate_registration([1, 2, 3], 2)