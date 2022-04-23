

class EmailNotUniqueError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class WrongEmailOrPassword(Exception):
    pass

class UserIsFollower(Exception):
    pass

class TripRequestNotFound(Exception):
    pass

class UserIsNotFollowed(Exception):
    pass