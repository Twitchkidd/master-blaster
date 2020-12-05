import requests
from vendor.lib.logging import logWarning

# networkActions #
# * Actions taken over the network. * #

# This defaults to v3 of the api.
GITHUB_API = "https://api.github.com"


def getRepos(username, token):
    """Get list of repos, validating token, or break the program, and log it."""
    """You can get a token of None now!!!"""
    repos = []
    if token == None:
        return username, token, repos
    url = f"{GITHUB_API}/user/repos"
    headers = {"Authorization": "token " + token}
    params = {"per_page": "1000", "type": "owner"}
    print("Checking for repos ...")
    response = requests.get(url, params=params, headers=headers)
    # Bad token returns a 401! #
    if response.status_code >= 400:
        print(
            f"Network error! Possibly the token! Try again please! If this is not your GitHub username, please restart the program: {username}"
        )
        logWarning(f"Response status: {response.status_code}")
        repos = None
    else:
        print("Repos received!")
        reposResponseConfirmed = True
        for repository in response.json():
            repos.append(
                {
                    "default": repository["default_branch"],
                    "htmlUrl": repository["html_url"],
                    "name": repository["name"],
                    "owner-login": f"{repository['owner']['login']}",
                }
            )
    return repos


def getBranchUrl(repo, branch):
    return f"{GITHUB_API}/repos/{repo['owner-login']}/{repo['name']}/branches/{branch}"


def checkRemoteBranches(token, repos):
    headers = {"Authorization": "token " + token}
    for repo in repos:
        targetBranchUrl = getBranchUrl(repo, repo["targetName"])
        masterBranchUrl = getBranchUrl(repo, "master")
        targetBranchResponse = requests.get(targetBranchUrl, headers=headers)
        masterBranchResponse = requests.get(masterBranchUrl, headers=headers)
        if targetBranchResponse.json().get("message"):
            repo["hasTarget"] = False
        if masterBranchResponse.json().get("message"):
            repo["hasMaster"] = False
        if targetBranchResponse.json().get("name"):
            repo["hasTarget"] = True
        if masterBranchResponse.json().get("name"):
            repo["hasMaster"] = True
    return repos