from vendor.lib.utils import Error


class SetBranchError(Error):
    """Raised when a branch can't be set. Should (not) be seen in testing.

    Attributes:
        errorMessage -- the stderr from the process
    """

    def __init__(self, errorMessage):
        self.message = (
            f"ERROR: Failed to set branch back! How'd we manage this? {errorMessage}"
        )


class NoRemotesError(Error):
    """Raised when there are no remotes for a repo.

    Attributes:
        None
    """

    def __init__(self):
        self.message = "ERROR: No remotes found for this repo!"


class NoUrlError(Error):
    """Raised when there's no url set for a repo's remote.

    Attributes:
        None
    """

    def __init__(self):
        self.message = "ERROR: No url set for this repo's remote! Program may only acts on local repos where the url matches a repo to act on."


class MultipleRemotesError(Error):
    """Raised when there are multiple remotes for a repo.

    Attributes:
        None
    """

    def __init__(self):
        self.message = "ERROR: Multiple remotes for this repo! Too complex for this version of `master-blaster`."


class MultipleLocalReposError(Error):
    """Raised when there are multiple local clones of a repo.

    Attributes:
        None
    """

    def __init__(self, name, directory, localPath):
        self.message = f"ERROR: Multiple local clones for {name}! Too complex for this version of `master-blaster`. First directory: {directory} Other directory: {localPath}"


class RenameBranchError(Error):
    """Raised when a branch can't be renamed.

    Attributes:
        directory -- the directory the process was run from, identifying the repo
        errorMessage -- the stderr from the process
    """

    def __init__(self, directory, errorMessage):
        self.message = (
            f"ERROR: Failed to rename branch from {directory}! {errorMessage}"
        )


class PushBranchRenameError(Error):
    """Raised when a rename can't be pushed to the remote.

    Attributes:
        directory -- the directory the process was run from, identifying the repo
        errorMessage -- the stderr from the process
    """

    def __init__(self, directory, errorMessage):
        self.message = f"ERROR: Failed to push branch name change to remote from {directory}! Attempting to move branch back to original! {errorMessage}"


class UpdateDefaultError(Error):
    """Raised when the default branch can't be updated on GitHub.

    Attributes:
        directory -- the directory the process was run from, identifying the repo
        errorMessage -- the stderr from the process
    """

    def __init__(self, directory, errorMessage):
        self.message = f"ERROR: Failed to change default branch on GitHub from {directory}! Attempting to move branch back to original and push branch name change to remote! {errorMessage}"


class DeleteRemoteError(Error):
    """Raised when the remote branch can't be deleted.

    Attributes:
        directory -- the directory the process was run from, identifying the repo
        errorMessage -- the stderr from the process
    """

    def __init__(self, branchName, directory, errorMessage):
        self.message = f"ERROR: Failed to delete branch on GitHub from {directory}! Attempting to move branch back to original and push branch name change to remote! {errorMessage}"


class MakeDirectoryError(Error):
    """Raised when the directory to clone a repo into can't be created.

    Attributes:
        directory -- the directory the process was run from
        errorMessage -- the stderr from the process
    """

    def __init__(self, directory, errorMessage):
        self.message = f"ERROR: Failed to make the directory to clone repos into from {directory}! {errorMessage}"


class CloneRepoError(Error):
    """Raised when a repo can't be cloned.

    Attributes:
        errorMessage -- the stderr from the process
    """

    def __init__(self, errorMessage):
        self.message = f"ERROR: Failed to clone repo! {errorMessage}"


class DeleteLocalError(Error):
    """Raised when a local branch can't be deleted.

    Attributes:
        branch -- what branch we were trying to delete
        directory -- the directory the process was run from
        errorMessage -- the stderr from the process
    """

    def __init__(self, branch, directory, errorMessage):
        self.message = (
            f"ERROR: Failed to delete {branch} branch from {directory}! {errorMessage}"
        )


class CheckoutError(Error):
    """Raised when a local branch can't be deleted.

    Attributes:
        branch -- what branch we were trying to check out
        directory -- the directory the process was run from
        errorMessage -- the stderr from the process
    """

    def __init__(self, branch, directory, errorMessage):
        self.message = f"ERROR: Failed to checkout {branch} branch from {directory}! {errorMessage}"


class FetchError(Error):
    """Raised when remote refs fail to be fetched.

    Attributes:
        directory -- the directory the process was run from
        errorMessage -- the stderr from the process
    """

    def __init__(self, directory, errorMessage):
        self.message = f"ERROR: Failed git fetch from {directory}! {errorMessage}"


class UnsetUpstreamError(Error):
    """Raised when removing the upstream information fails.

    Attributes:
        directory -- the directory the process was run from
        errorMessage -- the stderr from the process
    """

    def __init__(self, directory, errorMessage):
        self.message = f"ERROR: Failed to remove upstream information from {directory}! {errorMessage}"


class SetUpstreamError(Error):
    """Raised when setting the upstream information fails.

    Attributes:
        directory -- the directory the process was run from
        errorMessage -- the stderr from the process
    """

    def __init__(self, directory, errorMessage):
        self.message = f"ERROR: Failed to set upstream information from {directory}! {errorMessage}"


class UpdateRefError(Error):
    """Raised when updating the symbolic ref fails.

    Attributes:
        directory -- the directory the process was run from
        errorMessage -- the stderr from the process
    """

    def __init__(self, directory, errorMessage):
        self.message = (
            f"ERROR: Failed to update symbolic ref from {directory}! {errorMessage}"
        )


class RemoveClonesError(Error):
    """Raised when removing the cloned repos fails.

    Attributes:
        directory -- the directory the process was run from
        errorMessage -- the stderr from the process
    """

    def __init__(self, directory, errorMessage):
        self.message = (
            f"ERROR: Failed to remove cloned repos from {directory}! {errorMessage}"
        )


class GitNewError(Error):
    """Raised when adding the git alias fails.

    Attributes:
        errorMessage -- the stderr from the process
    """

    def __init__(self, errorMessage):
        self.message = f"ERROR: Failed to add git alias! {errorMessage}"
