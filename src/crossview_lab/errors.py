"""Domain errors presented by the command-line interface."""


class InputError(ValueError):
    """Raised when an input artifact does not satisfy the public contract."""
