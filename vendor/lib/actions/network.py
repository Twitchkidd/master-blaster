import json
import urllib
import requests
from vendor.lib.logging import logInfo
from vendor.lib.logging import logWarning

# networkActions #
# * Actions taken over the network. * #

# This defaults to v3 of the api.
GITHUB_API = "https://api.github.com"


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


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


def internet_on():
    """Pings Google to see if there's a network connection.

    Occasionally run and rehydrate this test:
        $ dig google.com +trace
    """
    try:
        urllib.request.urlopen("http://192.168.254.254", timeout=1)
        return True
    except urllib.error.URLError as err:
        return False


def getRepos(username, token):
    """Get list of repos, or throw an exception if the request fails (probably token.)"""
    repos = []
    url = f"{GITHUB_API}/user/repos"
    headers = {"Authorization": "token " + token}
    params = {"per_page": "1000", "type": "owner"}
    if not internet_on():
        raise NetworkError()
    print("Checking for repos ...")
    response = requests.get(url, params=params, headers=headers)
    # Bad token returns a 401! #
    if response.status_code >= 400:
        error_message = f"GitHub API request status code: {response.status_code}"
        raise RequestError(response.status_code, error_message)
    else:
        if len(response.json()) == 0:
            raise NoReposError()
        print("Repos received!\n")
        reposResponseConfirmed = True
        for repository in response.json():
            repos.append(
                {
                    "default": repository["default_branch"],
                    "htmlUrl": repository["html_url"],
                    "name": repository["name"],
                    "ownerLogin": f"{repository['owner']['login']}",
                }
            )
    return repos


def getBranchUrl(repo, branch):
    return f"{GITHUB_API}/repos/{repo['ownerLogin']}/{repo['name']}/branches/{branch}"


def checkRemoteBranches(token, repos):
    headers = {"Authorization": "token " + token}
    for repo in repos:
        targetBranchUrl = getBranchUrl(repo, repo["targetName"])
        masterBranchUrl = getBranchUrl(repo, "master")
        print(f"Checking {repo['name']} ...", end="")
        targetBranchResponse = requests.get(targetBranchUrl, headers=headers)
        masterBranchResponse = requests.get(masterBranchUrl, headers=headers)
        print(" got it!")
        if targetBranchResponse.json().get("message"):
            repo["hasTarget"] = False
        if masterBranchResponse.json().get("message"):
            repo["hasMaster"] = False
        if targetBranchResponse.json().get("name"):
            repo["hasTarget"] = True
        if masterBranchResponse.json().get("name"):
            repo["hasMaster"] = True
    return repos


def constructPatchDefaultUrl(ownerLogin, name):
    return f"{GITHUB_API}/repos/{ownerLogin}/{name}"


def updateDefaultBranch(token, repo):
    url = constructPatchDefaultUrl(repo["ownerLogin"], repo["name"])
    data = json.dumps({"default_branch": f"{repo['targetName']}"})
    headers = {"Authorization": "token " + token}
    patchDefaultResponse = requests.patch(url, data=data, headers=headers)
    if patchDefaultResponse.status_code >= 400:
        logWarning(
            f"{repo['htmlUrl']} default branch change failed, response status: {patchDefaultResponse.status_code}"
        )
        return f"Default branch change failed, response status: {patchDefaultResponse.status_code}"
    else:
        logInfo(
            f"Default branch for {repo['htmlUrl']} updated to {repo['targetName']}."
        )
        return None