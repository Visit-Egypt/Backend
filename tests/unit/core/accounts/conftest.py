from functools import partial

import pytest
from pytest_factoryboy import register
from tests.factories.entity_factories import (
    UserAuthBodyFactory,
    UserFactory,
)
from tests.factories.utils import make_many

FACTORIES = [
    UserAuthBodyFactory,
    UserFactory,
]

for factory in FACTORIES:
    register(factory)


@pytest.fixture()
def credentials(user_auth_body_factory):
    return user_auth_body_factory()


@pytest.fixture()
def many_credentials(user_auth_body_factory):
    return partial(make_many, user_auth_body_factory)


@pytest.fixture()
def user(user_factory):
    return user_factory()


@pytest.fixture()
def users(user_factory):
    return partial(make_many, user_factory)