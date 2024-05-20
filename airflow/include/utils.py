class APIError(Exception):
    """An exception for API errors."""
    def __init__(self, status_code, message="API request failed"):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} (status code: {self.status_code})'