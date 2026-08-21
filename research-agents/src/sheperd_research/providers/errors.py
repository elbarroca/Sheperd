class ProviderError(RuntimeError):
    """A provider failed without exposing credentials or response secrets."""

    attempts: list[dict[str, object]]
    error_code: str | None

    def __init__(
        self,
        message: str,
        *,
        attempts: list[dict[str, object]] | None = None,
        error_code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.attempts = list(attempts or [])
        self.error_code = error_code
