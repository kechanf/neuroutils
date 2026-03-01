"""Domain errors."""


class NeuroUtilsError(Exception):
    """Base package error."""


class SWCFormatError(NeuroUtilsError):
    """Raised for malformed SWC input."""


class ValidationError(NeuroUtilsError):
    """Raised when validation fails."""
