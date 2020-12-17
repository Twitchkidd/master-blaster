from vendor.lib.utils import Error


class RequestError(Error):
    """Raised when an operation attempts a GitHub API call that
    gets rejected.

    Attributes:
        status_code -- the response's status code
    """

    def __init__(self, status_code):
        self.message = f"ERROR: GitHub API request status code: {status_code}"


class NetworkError(Error):
    """Raised when there's no connection detected.

    Attributes:
        None.
    """

    def __init__(self):
        self.message = "ERROR: Not seeing an internet connection! Bailing out!"


class NoReposError(Error):
    """Raised when there's no repos to check against.

    Attributes:
        message -- explanation of what happened
    """

    def __init__(self):
        self.message = "Ending program: No repos to blast!"