import logging
from vendor.lib.utils import Error


class GetBranchError(Error):
    """Raised when a branch can't be gotten.

    Attributes:
        None.
    """

    def __init__(self):
        self.message = f"ERROR: Failed to get branch. Possible fix change directory into master-blaster root. {error_message}"


class SetBranchError(Error):
    """Raised when a branch can't be set.

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