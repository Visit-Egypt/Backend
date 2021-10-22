import pytest

from visitegypt.core.accounts.services import hash_service

@pytest.mark.unit
def test_hash_returns_hashed_value():
    value = "some value"
    result = hash_service.get_password_hash(value)
    second_result = hash_service.get_password_hash(value)

    assert result != value
    assert result != second_result


@pytest.mark.unit
def test_verify_valid_value():
    value = "some value"
    result = hash_service.get_password_hash(value)

    assert hash_service.verify_password(value, result)


@pytest.mark.unit
def test_verify_invalid_value():
    value = "some value"
    result = hash_service.get_password_hash("other value")

    assert not hash_service.verify_password(value, result)