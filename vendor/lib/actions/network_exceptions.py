from vendor.lib.utils import Error


class RequestError(Error):
    """Raised when an operation attempts a GitHub API call that
    gets rejected.

    Attributes:
        status_code -- the response's status code
    """

    def __init__(self, repoName, status_code):
        self.message = f"ERROR: Error with connection to GitHub API for {repoName}. Request status code: {status_code}"
        self.repoName = repoName


class NetworkConnectivityError(Error):
    """Raised when there's no connection detected.

    Attributes:
        None.
    """

    def __init__(self):
        self.message = "ERROR: Not seeing an internet connection! Bailing out!"


class NoReposError(Error):
    """Raised when there's no repos to check against.

    Attributes:
        None.
    """

    def __init__(self):
        self.message = "Ending program: No repos to blast!"