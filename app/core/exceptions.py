"""Custom exception classes."""


class AppException(Exception):
    """Base exception for custom exceptions."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class EntityNotFoundError(AppException):
    """Raised when an entity is not found in the database."""

    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            message=f"{entity_name} with id {entity_id} not found",
            status_code=404,
        )


class EntityAlreadyExistsError(AppException):
    """Raised when an entity already exists (e.g., duplicate email)."""

    def __init__(self, entity_name: str, field: str, value: str):
        super().__init__(
            message=f"{entity_name} with {field} {value} already exists",
            status_code=409,
        )


class InvalidCredentialsError(AppException):
    """Raised when credentials are invalid."""

    def __init__(self):
        super().__init__(
            message="Could not validate credentials",
            status_code=401,
        )


class ForbiddenError(AppException):
    """Raised when the user does not have permission to perform an action."""

    def __init__(self, message: str = "Not enough permissions"):
        super().__init__(message=message, status_code=403)


class UnauthorizedError(AppException):
    """Raised when the user is not authenticated."""

    def __init__(self, message: str = "Not authenticated"):
        super().__init__(message=message, status_code=401)