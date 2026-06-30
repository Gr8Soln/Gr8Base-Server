class DomainException(Exception):
    """Base class for all domain exceptions."""

class NotFoundError(DomainException):
    """Requested resource does not exist."""

class BusinessLogicError(DomainException):
    """Business rule violated."""


# =====- Auth Exceptions -=====-=====-=====-=====-=====
class AuthenticationError(DomainException):
    """Invalid credentials or token."""

class AuthorizationError(DomainException):
    """User lacks permission for the requested action."""
    
class AccountNotFoundError(DomainException):
    """Requested account does not exist."""

class InvalidTokenError(DomainException):
    """Token is invalid or has already been used."""

class ValidationError(DomainException):
    """Input or ownership validation failed."""

# =====- Infrastructure Exceptions -=====-=====-=====-=====
class DatabaseConnectionError(DomainException):
    """Database connection failed (e.g., provider quota exceeded, network issue)."""


class ExternalServiceQuotaError(DomainException):
    """An external service (database, email, cloud) has exceeded its quota limit."""

