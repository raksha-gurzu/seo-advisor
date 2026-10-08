"""Errors that the API turns into HTTP answers (see core/api.py)."""


class NotFoundError(LookupError):
    """The requested thing does not exist. The API answers 404 with the message."""


class InvalidInputError(ValueError):
    """A request value passed the schema but cannot be used. The API answers 422."""
