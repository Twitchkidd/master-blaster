import json
import logging
import urllib.request
import urllib.error
import requests
from vendor.lib.actions.network_exceptions import RequestError
from vendor.lib.actions.network_exceptions import NetworkConnectivityError
from vendor.lib.actions.network_exceptions import NoReposError

# This defaults to v3 of the api.
GITHUB_API = "https://api.github.com"


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


def get_repos(username, token):
    """Get list of repos, or throw an exception if the request fails (probably token.)"""
    repos = []
    url = f"{GITHUB_API}/user/repos"
    headers = {"Authorization": "token " + token}
    params = {"per_page": "1000", "type": "owner"}
    if not internet_on():
        raise NetworkConnectivityError()
    print("Checking for repos ...")
    response = requests.get(url, params=params, headers=headers)
    # Bad token returns a 401! #
    if response.status_code >= 400:
        raise RequestError(response.status_code)
    else:
        if len(response.json()) == 0:
            raise NoReposError()
        print("Repos received!\n")
        reposResponseConfirmed = True
        for repository in response.json():
            # ownerLogin is guaranteed to be the canonnical capitalization,
            # and it might look like we should just set username after getting
            # it, but the plan is to extend the option for different repo types
            repos.append(
                {
                    "name": repository["name"],
                    "ownerLogin": f"{repository['owner']['login']}",
                    "htmlUrl": repository["html_url"],
                    "gitUrl": repository["git_url"],
                    "sshUrl": repository["ssh_url"],
                    "default": repository["default_branch"],
                }
            )
    return repos


def get_branch_url(repo, branch):
    return f"{GITHUB_API}/repos/{repo['ownerLogin']}/{repo['name']}/branches/{branch}"


def check_remote_branches(token, repos):
    headers = {"Authorization": "token " + token}
    for repo in repos:
        try:
            if (
                repo["status"]
                == "Local folder that possibly isn't git repo, error opening .git/config from local directory."
                or repo["status"] == "Multiple remotes found in git config file."
            ):
                continue
        except KeyError:
            pass
        targetBranchUrl = get_branch_url(repo, repo["targetName"])
        masterBranchUrl = get_branch_url(repo, "master")
        print(f"Checking {repo['name']} ...", end="")
        targetBranchResponse = requests.get(targetBranchUrl, headers=headers)
        if (
            targetBranchResponse.status_code != 404
            and targetBranchResponse.status_code >= 400
        ):
            raise RequestError(targetBranchResponse.status_code)
        masterBranchResponse = requests.get(masterBranchUrl, headers=headers)
        if (
            masterBranchResponse.status_code != 404
            and masterBranchResponse.status_code >= 400
        ):
            raise RequestError(masterBranchResponse.status_code)
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


def construct_patch_default_url(ownerLogin, name):
    return f"{GITHUB_API}/repos/{ownerLogin}/{name}"


def update_default_branch(token, repo):
    url = construct_patch_default_url(repo["ownerLogin"], repo["name"])
    data = json.dumps({"default_branch": f"{repo['targetName']}"})
    headers = {"Authorization": "token " + token}
    patchDefaultResponse = requests.patch(url, data=data, headers=headers)
    if patchDefaultResponse.status_code >= 400:
        logging.warning(
            f"{repo['htmlUrl']} default branch change failed, response status: {patchDefaultResponse.status_code}"
        )
        return f"Default branch change failed, response status: {patchDefaultResponse.status_code}"
    else:
        logging.info(
            f"Default branch for {repo['htmlUrl']} updated to {repo['targetName']}."
        )
        return None