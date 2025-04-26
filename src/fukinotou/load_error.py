class LoadingError(Exception):
    def __init__(self, error_message: str, original_exception: Exception | None = None):
        self.error_message = error_message
        self.original_exception = original_exception

    def __str__(self) -> str:
        return f"Validation Error: details {self.error_message}"
