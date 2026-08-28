"""Domain-specific exceptions for Geosquare V2."""


class GeosquareError(Exception):
    """Base class for all Geosquare V2 errors."""


class ValidationError(GeosquareError, ValueError):
    """Raised when an input does not satisfy the V2 contract."""


class UnknownDomainError(GeosquareError, KeyError):
    """Raised when a requested domain is not present in a registry."""


class OutOfDomainError(GeosquareError, ValueError):
    """Raised when projected coordinates are outside a profile root square."""


class InvalidGIDError(ValidationError):
    """Raised when a GID is malformed or invalid at its declared level."""


class InvalidPackedIDError(ValidationError):
    """Raised when an Int64 value cannot encode a valid V2 cell."""


class RegistryDependencyError(GeosquareError, ImportError):
    """Raised when optional signed-registry dependencies are unavailable."""


class GeometryDependencyError(GeosquareError, ImportError):
    """Raised when optional geometry dependencies are unavailable."""


class CandidateLimitExceededError(GeosquareError, ValueError):
    """Raised before polyfill enumeration exceeds its declared candidate limit."""


class ManifestValidationError(GeosquareError, ValueError):
    """Raised when a signed registry artifact violates the V2 release contract."""


class ManifestSignatureError(ManifestValidationError):
    """Raised when a manifest signature cannot be verified with a trusted key."""


class ArtifactHashMismatchError(ManifestValidationError):
    """Raised when an artifact does not match its signed SHA-256 digest."""


class ProjResourceVerificationError(ManifestValidationError):
    """Raised when installed PROJ resources differ from the signed release requirements."""
