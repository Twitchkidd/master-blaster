class Error(Exception):
    """Base class for exceptions in this module."""

    pass


states = {
    "mvThirdToTarget": "Move third to target.",
    "deleteMaster": "Delete master.",
    "localUpdateProcess": "Local update process.",
    "remoteProcess": "Remote process.",
    "alreadyBlasted": "Already blasted.",
    "multipleLocals": "Multiple local repos.",
    "multipleRemotes": "Multiple remotes found in git config file.",
    "gitBranchError": "There was an error running git branch when checking the local repo.",
    "rejectedResponse": "API call rejected.",
    "pathUnclear": "Path unclear.",
}
