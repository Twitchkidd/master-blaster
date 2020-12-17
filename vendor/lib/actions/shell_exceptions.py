from vendor.lib.utils import Error


class GetBranchError(Error):
    """Raised when a branch can't be gotten, should only be seen in testing.

    Attributes:
        None.
    """

    def __init__(self):
        self.message = f"ERROR: Failed to get branch. Possible fix: change to master-blaster directory."


class SetBranchError(Error):
    """Raised when a branch can't be set. Should (not) be seen in testing.

    Attributes:
        error_message -- the stderr from the process
    """

    def __init__(self, error_message):
        self.message = (
            f"ERROR: Failed to set branch back! How'd we manage this? {error_message}"
        )


class RenameBranchError(Error):
    """Raised when a branch can't be renamed.

    Attributes:
        error_message -- the stderr from the process"""

    def __init__(self, error_message):
        self.message = f"ERROR: Failed to rename branch! {error_message}"