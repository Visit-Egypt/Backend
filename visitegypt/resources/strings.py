# API messages

USER_DOES_NOT_EXIST_ERROR = "User does not exist"

INCORRECT_LOGIN_INPUT = "Incorrect email or password"
USERNAME_TAKEN = "User with this username already exists"
EMAIL_TAKEN = "User with this email already exists"

WRONG_TOKEN_PREFIX = "Unsupported authorization type"
MALFORMED_PAYLOAD = "Could not validate credentials"

AUTHENTICATION_REQUIRED = "authentication required"
USER_DELETED = "User is deleted"
PLACE_DELETED = "Place is deleted"
POST_DELETED = "Post is deleted"


def MESSAGE_404(m: str):
    return f"{m} not exist"
