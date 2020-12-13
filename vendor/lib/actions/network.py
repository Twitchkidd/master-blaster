import json
import requests
from vendor.lib.logging import logInfo
from vendor.lib.logging import logWarning

# networkActions #
# * Actions taken over the network. * #

# This defaults to v3 of the api.
GITHUB_API = "https://api.github.com"


def getRepos(username, token):
    """Get list of repos, or throw an exception if the request fails (probably token.)"""
    repos = []
    url = f"{GITHUB_API}/user/repos"
    headers = {"Authorization": "token " + token}
    params = {"per_page": "1000", "type": "owner"}
    print("Checking for repos ...")
    response = requests.get(url, params=params, headers=headers)
    # Bad token returns a 401! #
    if response.status_code >= 400:
        # raise RequestFailure(f"thatString")
        print(
            f"Network error! Possibly the token! Try again please! If this is not your GitHub username, please restart the program: {username}"
        )
        logWarning(f"Response status: {response.status_code}")
        return None
    else:
        if len(response.json()) == 0:
            print("No repos to blast!")
            raise TYPE?!
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