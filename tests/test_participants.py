import pytest
from pydantic import ValidationError
from app.schemas import Participant
from app.services import has_available_capacity, check_duplicate_registration


# ---------- Happy path ----------
def test_valid_participant_creation(sample_participant_dict):
    p = Participant(**sample_participant_dict)
    assert p.name == "Amine"
    assert p.email == "amine@example.com"


def test_capacity_available():
    assert has_available_capacity(10, 100) is True


def test_no_duplicate_passes_silently():
    assert check_duplicate_registration([1, 2, 3], 4) is None


# ---------- Boundary values ----------
def test_capacity_current_is_max_minus_one():
    assert has_available_capacity(99, 100) is True


def test_capacity_current_equals_max():
    assert has_available_capacity(100, 100) is False


def test_capacity_current_exceeds_max():
    assert has_available_capacity(101, 100) is False


def test_name_length_exactly_two(sample_participant_dict):
    sample_participant_dict["name"] = "Al"
    assert Participant(**sample_participant_dict).name == "Al"


# ---------- Negative ----------
@pytest.mark.parametrize("bad_email", ["plainaddress", "no@tld", "@x.com", "a b@x.com"])
def test_invalid_email_rejected(sample_participant_dict, bad_email):
    sample_participant_dict["email"] = bad_email
    with pytest.raises(ValidationError):
        Participant(**sample_participant_dict)


def test_short_name_rejected(sample_participant_dict):
    sample_participant_dict["name"] = "A"
    with pytest.raises(ValidationError):
        Participant(**sample_participant_dict)


def test_duplicate_registration_raises():
    with pytest.raises(ValueError):
        check_duplicate_registration([1, 2, 3], 2)
