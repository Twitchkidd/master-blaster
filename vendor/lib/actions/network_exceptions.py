from vendor.lib.utils import Error


class RequestError(Error):
    """Raised when an operation attempts a GitHub API call that
    gets rejected.

    Attributes:
        status_code -- the response's status code
        message -- explanation of what happened
    """

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message


class NetworkError(Error):
    """Raised when there's no connection detected.

    Attributes:
        message -- explanation of what happened
    """

    def __init__(self, message="Not seeing an internet connection! Bailing out!"):
        self.message = message


class NoReposError(Error):
    """Raised when there's no repos to check against.

    Attributes:
        message -- explanation of what happened
    """

    def __init__(self, message="No repos to blast!"):
        self.message = message