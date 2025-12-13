"""
Custom exceptions for the application.

These exceptions provide domain-specific error handling and allow for
consistent error responses across the application.
"""

class ApplicationException(Exception):
    """Base exception class for the application errors."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class NotFoundError(ApplicationException):
    """Exception raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)

class ConflictError(ApplicationException):
    """Exception raised when there is a conflict with the current state of the resource."""

    def __init__(self, message: str = "Conflict with the current state of the resource"):
        super().__init__(message, status_code=409)

class ValidationError(ApplicationException):
    """Exception raised for validation errors."""

    def __init__(self, message: str = "Validation error occurred"):
        super().__init__(message, status_code=422)

class UnauthorizedError(ApplicationException):
    """Exception raised for unauthorized access attempts."""

    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, status_code=401)


class ForbiddenError(ApplicationException):
    """Exception raised for forbidden access attempts."""

    def __init__(self, message: str = "Forbidden access"):
        super().__init__(message, status_code=403)


class InternalServerError(ApplicationException):
    """Exception raised for internal server errors."""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status_code=500)


class BadRequestError(ApplicationException):
    """Exception raised for bad request errors."""

    def __init__(self, message: str = "Bad request"):
        super().__init__(message, status_code=400)

class ServiceUnavailableError(ApplicationException):
    """Exception raised when the service is unavailable."""

    def __init__(self, message: str = "Service unavailable"):
        super().__init__(message, status_code=503)


class RequestTimeoutError(ApplicationException):
    """Exception raised when a request times out."""

    def __init__(self, message: str = "Request timed out"):
        super().__init__(message, status_code=504)


class DependencyError(ApplicationException):
    """Exception raised when a dependency fails."""

    def __init__(self, message: str = "Dependency error occurred"):
        super().__init__(message, status_code=424)

        
class RateLimitExceededError(ApplicationException):
    """Exception raised when the rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)

