from faker import factory
from tests.factories.providers import PasswordHashProvider
from visitegypt.core.accounts.entities.user import User, UserResponse
from visitegypt.core.authentication.entities.userauth import UserAuthBody

# Register providers
providers = [PasswordHashProvider]

for provider in providers:
    factory.Faker.add_provider(provider)


# User
class UserAuthBodyFactory(factory.Factory):
    class Meta:
        model = UserAuthBody

    email = factory.Faker("email")
    password = factory.Faker("password", length=16)


class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Faker("email")
    hashed_password = factory.Faker("password_hash")
    first_name = factory.Faker("pystr", min_chars=3, max_chars=50)
    last_name = factory.Faker("pystr", min_chars=3, max_chars=50)
    phone_number = factory.Faker("phone_number", min_chars=3, max_chars=50)


class UserResponseFactory(factory.Factory):
    class Meta:
        model = UserResponse

    email = factory.Faker("email")
    first_name = factory.Faker("pystr", min_chars=3, max_chars=50)
    last_name = factory.Faker("pystr", min_chars=3, max_chars=50)
    phone_number = factory.Faker("phone_number", min_chars=3, max_chars=50)
    id = factory.Faker("pystr", min_chars=20, max_chars=50)
    user_role = factory.Faker("pystr", min_chars=5, max_chars=7)
