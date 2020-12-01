

import importlib
import json
import logging
import os
from pathlib import Path
from subprocess import Popen, PIPE

# what if you appended with Path, like
# sys.path.append(Path.cwd() / "vendor")

# Add vendor directory to module search path
parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, "vendor")

sys.path.append(vendor_dir)

import questionary
import requests

# This defaults to v3 of the api.
GITHUB_API = "https://api.github.com"

# if repoTypes in [
#     repoTypesAll,
#     repoTypesOwner,
#     repoTypesCollaborator,
#     repoTypesOrganization,
# ]:
#     tokenType = "repo"
# else:
#     tokenType = "public repo"
# simple === "repo"


# * ``` Placeholder variable for the total set of repos! ``` * #
repos = []

# * ``` Ask for the token until the response comes back okay, then extract the data from the API call! ``` * #
reposResponseConfirmed = False
while not reposResponseConfirmed:
    token = getToken()
    url = constructReposUrl()
    params = constructReposParams()
    headers = constructHeaders(token)
    print("Checking for repos ...")
    # >> right here, the token/initial auth part needs to be ahead of the options part,
    # >> so we need a requests.get(url, params={simpler}, headers={simple}) here
    reposResponse = requests.get(url, params=params, headers=headers)
    # Bad token returns a 401! #
    if reposResponse.status_code >= 400:
        logging.warning(f"Response status: {reposResponse.status_code}")
        print(
            f"Network error! Possibly the token! Try again please! If this is not your GitHub username, please restart the program: {username}"
        )
        continue
    else:
        print("Repos received!")
        reposResponseConfirmed = True
        for repository in reposResponse.json():
            repos.append(
                {
                    "defaultBranch": repository["default_branch"],
                    "htmlUrl": repository["html_url"],
                    "name": repository["name"],
                    "owner-login": f"{repository['owner']['login']}",
                    "primaryBranchName": name,
                }
            )
        pass


# * If they wanted to name each primary branch, do so now! * #
if interactive:
    print(
        """
        Interactive naming mode!
    """
    )
    for repo in repos:
        primaryBranchNameConfirmed = False
        while not primaryBranchNameConfirmed:
            repoNameResponse = questionary.text(
                f"Primary branch name for {repo['htmlUrl']}?"
            ).ask()
            if repoNameResponse == "":
                defaultNameResponse = questionary.confirm(
                    f"Default primary branch name {name} for {repo['htmlUrl']}?"
                )
                if defaultNameResponse:
                    logging.info(f"Primary branch name for {repo['htmlUrl']}: {name}")
                    primaryBranchNameConfirmed = True
                    continue
                else:
                    continue
            else:
                customRepoNameConfirmed = questionary.confirm(
                    f"{repoNameResponse} for {repo['htmlUrl']}?"
                )
                if customRepoNameConfirmed:
                    primaryBranchNameConfirmed = True
                    repo["primaryBranchName"] = repoNameResponse
                    logging.info(
                        f"Primary branch name for {repo['htmlUrl']}: {repoNameResponse}"
                    )
                    continue
                else:
                    pass


# * ~~~ Take all these repos and test them against what the name is supposed to be! ~~~ * #

# * ``` Construct the url! ``` * #
def constructBranchesUrl(repo, which):
    return f"{GITHUB_API}/repos/{repo['owner-login']}/{repo['name']}/branches/{which}"


# * ``` Check each remote to see if they have master branches or branches with the name already! ``` * #
for repo in repos:
    primaryBranchUrl = constructBranchesUrl(repo, repo["primaryBranchName"])
    masterBranchUrl = constructBranchesUrl(repo, "master")
    headers = constructHeaders(token)
    print(f"Checking branches for {repo['htmlUrl']}.")
    primaryBranchResponse = requests.get(primaryBranchUrl, headers=headers)
    masterBranchResponse = requests.get(masterBranchUrl, headers=headers)
    if primaryBranchResponse.json().get("message"):
        repo["hasPrimaryBranchName"] = False
    if masterBranchResponse.json().get("message"):
        repo["hasMasterBranch"] = False
    if primaryBranchResponse.json().get("name"):
        repo["hasPrimaryBranchName"] = True
    if masterBranchResponse.json().get("name"):
        repo["hasMasterBranch"] = True


# * ~~~ If they wanted to use local clones, look for them! ~~~ * #

# * ``` Placeholder variable for the set of local repos! ``` * #
localRepos = []


# * ``` Check got config file for remote url! ``` * #
def getLocalRepoUrl(configFile):
    url = ""
    for line in configFile:
        if line.find("url =") != -1:
            remoteOriginUrlStart = line.find("url =")
            url = line[remoteOriginUrlStart + 6 : -1]
            return url


# * ``` Find all local repos that share a name with the repos to change! (Url is test for owner!) ``` * #
if localDirectories:
    repoNames = [repo["name"] for repo in repos]
    for root, subdirs, files in os.walk(f"{localDirectory}"):
        for subdir in subdirs:
            if any(subdir == repoName for repoName in repoNames):
                try:
                    with open(f"{root}/{subdir}/.git/config", "r") as configFile:
                        localRepos.append(
                            {
                                "url": getLocalRepoUrl(configFile).lower(),
                                "path": f"{root}/{subdir}",
                                "branch": f"{get_active_branch_name(f'{root}/{subdir}')}",
                            }
                        )
                except Exception as err:
                    # print(f"Exception: {err}")
                    pass

# * ~~~ Change the branches! ~~~ * #

# * ``` The set of local repo origin urls! ``` * #
localRepoUrls = [localRepo["url"] for localRepo in localRepos]

# * ``` Placeholder variables for groups of checked repos! ``` * #
reposAlreadyBlasted = []
reposWithErrors = []
reposReadyForLocal = []
reposReadyForLocalMasterDelete = []
reposReadyForRemote = []

# * ``` Take in the state of the branch names and defaults and categorize them! ``` * #


def check(repo):
    if repo["hasMasterBranch"] and repo["hasPrimaryBranchName"]:
        repo[
            "status"
        ] = "error: remote has both master branch and new primary branch name"
        reposWithErrors.append(repo)
        return None
    if not repo["hasMasterBranch"] and not repo["hasPrimaryBranchName"]:
        repo["status"] = "error: remote has neither master nor new primary branch name"
        reposWithErrors.append(repo)
        return None
    if repo.get("localHasPrimaryBranchName") != None:
        if (
            not repo["hasMasterBranch"]
            and repo["hasPrimaryBranchName"]
            and repo["defaultBranch"] == repo["primaryBranchName"]
            and not repo["localHasMaster"]
            and repo["localHasPrimaryBranchName"]
        ):
            repo["status"] = "already blasted"
            reposAlreadyBlasted.append(repo)
            return None
        if (
            not repo["hasMasterBranch"]
            and repo["hasPrimaryBranchName"]
            and repo["defaultBranch"] == repo["primaryBranchName"]
            and repo["localHasMaster"]
            and repo["localHasPrimaryBranchName"]
        ):
            repo["status"] = "candidate to delete local master"
            reposReadyForLocalMasterDelete.append(repo)
            return None
        if repo["localHasMaster"] and not repo["localHasPrimaryBranchName"]:
            if (
                not repo["hasMasterBranch"]
                and repo["hasPrimaryBranchName"]
                and repo["defaultBranch"] == repo["primaryBranchName"]
            ):
                repo["status"] = "candidate for local process"
                reposReadyForLocal.append(repo)
                return None
            if (
                repo["hasMasterBranch"]
                and not repo["hasPrimaryBranchName"]
                and repo["defaultBranch"] == "master"
            ):
                repo["status"] = "candidate for remote process"
                reposReadyForRemote.append(repo)
                return None
        if (
            repo["defaultBranch"] != repo["primaryBranchName"]
            and repo["defaultBranch"] != "master"
        ):
            repo[
                "status"
            ] = f"Primary branch neither {repo['primaryBranchName']} nor master"
            reposWithErrors.append(repo)
            return None
        repo["status"] = f"error: {repo}"
        reposWithErrors.append(repo)
        return None
    else:
        if (
            not repo["hasMasterBranch"]
            and repo["hasPrimaryBranchName"]
            and repo["defaultBranch"] == repo["primaryBranchName"]
        ):
            repo["status"] = "already blasted"
            reposAlreadyBlasted.append(repo)
            return None
        if (
            repo["hasMasterBranch"]
            and not repo["hasPrimaryBranchName"]
            and repo["defaultBranch"] == "master"
        ):
            repo["status"] = "candidate for remote process"
            reposReadyForRemote.append(repo)
            return None
        if (
            repo["defaultBranch"] != repo["primaryBranchName"]
            and repo["defaultBranch"] != "master"
        ):
            repo[
                "status"
            ] = f"Primary branch neither {repo['primaryBranchName']} nor master"
            reposWithErrors.append(repo)
            return None
    repo["status"] = f"error: {repo}"
    reposWithErrors.append(repo)
    return None


def processLogger(string, prc, ignoreStr="", secondIgnoreStr=""):
    """Log what process is being run and stdout, return of 0 is good, 1 is error"""
    logging.info(string)
    stdout, stderr = prc.communicate()
    if len(stdout) > 0:
        logging.info(stdout)
    if len(stderr) > 0:
        if ignoreStr != "" and ignoreStr in stderr.decode():
            logging.warning(stderr)
            logging.info("You may be able to ignore the above warning.")
            return (stdout, stderr, 0)
        logging.warning(stderr)
        return (stdout, stderr, 1)
    return (stdout, stderr, 0)


# * ``` Check all the repos! (And prepare any locals for the check!) ``` * #
if localDirectories:
    print("Checking repos ...")
    for repo in repos:
        if f"{repo['htmlUrl']}.git".lower() in localRepoUrls:
            localPath = ""
            for localRepo in localRepos:
                if localRepo["url"] == f"{repo['htmlUrl']}.git".lower():
                    localPath = localRepo["path"]
            localBranchInfoGitBranch = Popen(
                ["git", "branch"], cwd=localPath, stdout=PIPE, stderr=PIPE
            )
            localBranchInfoGitBranchStdout = processLogger(
                f"cwd={localPath}: git branch", localBranchInfoGitBranch
            )[0]
            repo["localHasMaster"] = "master" in f"{localBranchInfoGitBranchStdout}"
            repo["localHasPrimaryBranchName"] = (
                repo["primaryBranchName"] in f"{localBranchInfoGitBranchStdout}"
            )
            check(repo)
        else:
            check(repo)
else:
    print("Checking repos ...")
    for repo in repos:
        check(repo)

# * ``` Placeholder variable for local and remote processes being a go! ``` * #
localIsAGo = False
localMasterDeleteIsAGo = False
remoteIsAGo = False


# * ``` Update local repo that still has master to sync with remote that already has the chosen name! ``` * #
def localProcess(repo):
    for localRepo in localRepos:
        if f"{repo['htmlUrl']}.git".lower() == localRepo["url"]:
            localProcessGcm = Popen(
                ["git", "checkout", "master"],
                cwd=localRepo["path"],
                stdout=PIPE,
                stderr=PIPE,
            )
            processLogger(
                f"cwd={localRepo['path']}: git checkout master",
                localProcessGcm,
                ignoreStr="Already on",
                secondIgnoreStr="Switched to",
            )
            localProcessGbm = Popen(
                ["git", "branch", "-m", "master", repo["primaryBranchName"]],
                cwd=localRepo["path"],
                stdout=PIPE,
                stderr=PIPE,
            )
            processLogger(
                f"cwd={localRepo['path']}: git branch -m master {repo['primaryBranchName']}",
                localProcessGbm,
            )
            localProcessGf = Popen(
                ["git", "fetch"], cwd=localRepo["path"], stdout=PIPE, stderr=PIPE
            )
            localProcessGfExitCode = processLogger(
                f"cwd={localRepo['path']}: git fetch", localProcessGf, ignoreStr="From"
            )[2]
            if localProcessGfExitCode == 1:
                repo["error"] = True
                return
            localProcessGbuu = Popen(
                ["git", "branch", "--unset-upstream"],
                cwd=localRepo["path"],
                stdout=PIPE,
                stderr=PIPE,
            )
            processLogger(
                f"cwd={localRepo['path']}: git branch --unset-upstream",
                localProcessGbuu,
            )
            localProcessGbuo = Popen(
                ["git", "branch", "-u", f"origin/{repo['primaryBranchName']}"],
                cwd=localRepo["path"],
                stdout=PIPE,
                stderr=PIPE,
            )
            localProcessGbuoExitCode = processLogger(
                f"cwd={localRepo['path']}: git branch -u origin/{repo['primaryBranchName']}",
                localProcessGbuo,
                ignoreStr="To",
            )[2]
            if localProcessGbuoExitCode == 1:
                repo["error"] = True
                return
            localProcessGsro = Popen(
                [
                    "git",
                    "symbolic-ref",
                    "refs/remotes/origin/HEAD",
                    f"refs/remotes/origin/{repo['primaryBranchName']}",
                ],
                cwd=localRepo["path"],
                stdout=PIPE,
                stderr=PIPE,
            )
            processLogger(
                f"cwd={localRepo['path']}: git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/{repo['primaryBranchName']}",
                localProcessGsro,
            )


# * ``` Delete stray master branch! ``` * #


def localMasterDeleteProcess(repo):
    for localRepo in localRepos:
        if f"{repo['htmlUrl']}.git".lower() == localRepo["url"]:
            localMasterDeleteProcessCheckoutPrimary = Popen(
                ["git", "checkout", f"{repo['primaryBranchName']}"],
                cwd=localRepo["path"],
                stdout=PIPE,
                stderr=PIPE,
            )
            localMasterDeleteProcessCheckoutPrimaryExitCode = processLogger(
                f"cwd={localRepo['path']}: git checkout {repo['primaryBranchName']}",
                localMasterDeleteProcessCheckoutPrimary,
                ignoreStr="Already on",
                secondIgnoreStr="Switched to",
            )[2]
            if localMasterDeleteProcessCheckoutPrimaryExitCode == 1:
                repo["error"] = True
                return
            localMasterDeleteProcessBranchD = Popen(
                ["git", "branch", "-d", "master"],
                cwd=localRepo["path"],
                stdout=PIPE,
                stderr=PIPE,
            )
            processLogger(
                f"cwd={localRepo['path']}: git branch -d master",
                localMasterDeleteProcessBranchD,
            )
            localMasterDeleteProcessCheckoutPrevious = Popen(
                ["git", "checkout", f"{localRepo['branch']}"],
                cwd=localRepo["path"],
                stdout=PIPE,
                stderr=PIPE,
            )
            processLogger(
                f"cwd={localRepo['path']}: git checkout {localRepo['branch']}",
                localMasterDeleteProcessCheckoutPrevious,
                ignoreStr="Already on",
                secondIgnoreStr="Switched to",
            )


# * ``` Update remote repo that still has master! ``` * #


def constructPatchDefaultUrl(repo):
    return f"{GITHUB_API}/repos/{repo['owner-login']}/{repo['name']}"


def remoteProcess(repo):
    if localDirectories:
        if f"{repo['htmlUrl']}.git".lower() in localRepoUrls:
            for localRepo in localRepos:
                if f"{repo['htmlUrl']}.git".lower() == localRepo["url"]:
                    remoteProcessLocalRepoGbm = Popen(
                        ["git", "branch", "-m", "master", repo["primaryBranchName"]],
                        cwd=localRepo["path"],
                        stdout=PIPE,
                        stderr=PIPE,
                    )
                    processLogger(
                        f"cwd={localRepo['path']}: git branch -m master {repo['primaryBranchName']}",
                        remoteProcessLocalRepoGbm,
                    )
                    remoteProcessLocalRepoGpuo = Popen(
                        ["git", "push", "-u", "origin", repo["primaryBranchName"]],
                        cwd=localRepo["path"],
                        stdout=PIPE,
                        stderr=PIPE,
                    )
                    remoteProcessLocalRepoGpuoExitCode = processLogger(
                        f"cwd={localRepo['path']}: git push -u origin {repo['primaryBranchName']}",
                        remoteProcessLocalRepoGpuo,
                        ignoreStr="To",
                    )[2]
                    if remoteProcessLocalRepoGpuoExitCode == 1:
                        repo["error"] = True
                        return
                    url = constructPatchDefaultUrl(repo)
                    data = json.dumps(
                        {"default_branch": f"{repo['primaryBranchName']}"}
                    )
                    headers = constructHeaders(token)
                    patchDefaultResponse = requests.patch(
                        url, data=data, headers=headers
                    )
                    if patchDefaultResponse.status_code >= 400:
                        logging.warning(
                            f"{repo['htmlUrl']} default branch change failed, response status: {patchDefaultResponse.status_code}"
                        )
                        repo["error"] = True
                        return
                    else:
                        logging.info(
                            f"Default branch for {repo['htmlUrl']} updated to {repo['primaryBranchName']}."
                        )
                        remoteProcessLocalRepoGpdm = Popen(
                            ["git", "push", "--delete", "origin", "master"],
                            cwd=f"{localRepo['path']}",
                            stdout=PIPE,
                            stderr=PIPE,
                        )
                        remoteProcessLocalRepoGpdmExitCode = processLogger(
                            f"cwd={localRepo['path']}: git push --delete origin master",
                            remoteProcessLocalRepoGpdm,
                            ignoreStr="To",
                        )[2]
                        if remoteProcessLocalRepoGpdmExitCode == 1:
                            repo["error"] = True
                            return
        else:
            if not os.path.isdir(f"{localDirectory}/master-blaster-{username}/"):
                remoteProcessRemoteRepoMkdir = Popen(
                    ["mkdir", "-pv", f"{localDirectory}/master-blaster-{username}/"],
                    cwd=localDirectory,
                    stdout=PIPE,
                    stderr=PIPE,
                )
                remoteProcessRemoteRepoMkdirExitCode = processLogger(
                    f"cwd={localDirectory}: mkdir -pv {localDirectory}/master-blaster-{username}/",
                    remoteProcessRemoteRepoMkdir,
                )[2]
                if remoteProcessRemoteRepoMkdirExitCode == 1:
                    logging.warning("Error making temp dir!")
                    repo["error"] = True
                    return
            remoteProcessRemoteRepoGcl = Popen(
                [
                    "git",
                    "clone",
                    f"{repo['htmlUrl']}.git",
                    f"./{repo['owner-login']}/{repo['name']}",
                ],
                cwd=f"{localDirectory}/master-blaster-{username}/",
                stdout=PIPE,
                stderr=PIPE,
            )
            remoteProcessRemoteRepoGclExitCode = processLogger(
                f"cwd={localDirectory}/master-blaster-{username}/: git clone {repo['htmlUrl']}.git ./{repo['owner-login']}/{repo['name']}",
                remoteProcessRemoteRepoGcl,
                ignoreStr="Cloning",
            )[2]
            if remoteProcessRemoteRepoGclExitCode == 1:
                repo["error"] = True
                return
            remoteProcessRemoteRepoGbm = Popen(
                ["git", "branch", "-m", "master", repo["primaryBranchName"]],
                cwd=f"{localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}",
                stdout=PIPE,
                stderr=PIPE,
            )
            processLogger(
                f"cwd={localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}: git branch -m master {repo['primaryBranchName']}",
                remoteProcessRemoteRepoGbm,
            )
            remoteProcessRemoteRepoGpuo = Popen(
                ["git", "push", "-u", "origin", repo["primaryBranchName"]],
                cwd=f"{localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}",
                stdout=PIPE,
                stderr=PIPE,
            )
            remoteProcessRemoteRepoGpuoExitCode = processLogger(
                f"cwd={localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}: git push -u origin {repo['primaryBranchName']}",
                remoteProcessRemoteRepoGpuo,
                ignoreStr="To",
            )[2]
            if remoteProcessRemoteRepoGpuoExitCode == 1:
                repo["error"] = True
                return
            url = constructPatchDefaultUrl(repo)
            data = json.dumps({"default_branch": f"{repo['primaryBranchName']}"})
            headers = constructHeaders(token)
            patchDefaultResponse = requests.patch(url, data=data, headers=headers)
            if patchDefaultResponse.status_code >= 400:
                logging.warning(
                    f"{repo['htmlUrl']} default branch change failed, response status: {patchDefaultResponse.status_code}"
                )
                repo["error"] = True
                return
            else:
                logging.info(
                    f"Default branch for {repo['htmlUrl']} updated to {repo['primaryBranchName']}."
                )
                remoteProcessGpdm = Popen(
                    ["git", "push", "--delete", "origin", "master"],
                    cwd=f"{localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}",
                    stdout=PIPE,
                    stderr=PIPE,
                )
                remoteProcessGpdmExitCode = processLogger(
                    f"cwd={localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}: git push --delete origin master",
                    remoteProcessGpdm,
                    ignoreStr="To",
                )[2]
                if remoteProcessGpdmExitCode == 1:
                    repo["error"] = True
                    return
    else:
        if not os.path.isdir(f"{localDirectory}/master-blaster-{username}/"):
            remoteProcessRemoteRepoMkdir = Popen(
                ["mkdir", "-pv", f"{localDirectory}/master-blaster-{username}/"],
                cwd=localDirectory,
                stdout=PIPE,
                stderr=PIPE,
            )
            remoteProcessRemoteRepoMkdirExitCode = processLogger(
                f"cwd={localDirectory}: mkdir -pv {localDirectory}/master-blaster-{username}/",
                remoteProcessRemoteRepoMkdir,
            )[2]
            if remoteProcessRemoteRepoMkdirExitCode == 1:
                logging.warning("Error making temp dir!")
                repo["error"] = True
                return
        remoteProcessRemoteRepoGcl = Popen(
            [
                "git",
                "clone",
                f"{repo['htmlUrl']}.git",
                f"./{repo['owner-login']}/{repo['name']}",
            ],
            cwd=f"{localDirectory}/master-blaster-{username}",
            stdout=PIPE,
            stderr=PIPE,
        )
        remoteProcessRemoteRepoGclExitCode = processLogger(
            f"cwd={localDirectory}/master-blaster-{username}: git clone {repo['htmlUrl']}.git ./{repo['owner-login']}/{repo['name']}",
            remoteProcessRemoteRepoGcl,
            ignoreStr="Cloning",
        )[2]
        if remoteProcessRemoteRepoGclExitCode == 1:
            repo["error"] = True
            return
        remoteProcessRemoteRepoGbm = Popen(
            ["git", "branch", "-m", "master", repo["primaryBranchName"]],
            cwd=f"{localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}",
            stdout=PIPE,
            stderr=PIPE,
        )
        processLogger(
            f"cwd={localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}: git branch -m master {repo['primaryBranchName']}",
            remoteProcessRemoteRepoGbm,
        )
        remoteProcessRemoteRepoGpuo = Popen(
            ["git", "push", "-u", "origin", repo["primaryBranchName"]],
            cwd=f"{localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}",
            stdout=PIPE,
            stderr=PIPE,
        )
        remoteProcessRemoteRepoGpuoExitCode = processLogger(
            f"cwd={localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}: git branch -u origin {repo['primaryBranchName']}",
            remoteProcessRemoteRepoGpuo,
            ignoreStr="To",
        )[2]
        if remoteProcessRemoteRepoGpuoExitCode == 1:
            repo["error"] = True
            return
        url = constructPatchDefaultUrl(repo)
        data = json.dumps({"default_branch": f"{repo['primaryBranchName']}"})
        headers = constructHeaders(token)
        patchDefaultResponse = requests.patch(url, data=data, headers=headers)
        if patchDefaultResponse.status_code >= 400:
            logging.warning(
                f"{repo['htmlUrl']} default branch change failed, response status: {patchDefaultResponse.status_code}"
            )
            repo["error"] = True
            return
        else:
            logging.info(
                f"Default branch for {repo['htmlUrl']} updated to {repo['primaryBranchName']}."
            )
            remoteProcessGpdm = Popen(
                ["git", "push", "--delete", "origin", "master"],
                cwd=f"{localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}",
                stdout=PIPE,
                stderr=PIPE,
            )
            remoteProcessGpdmExitCode = processLogger(
                f"cwd={localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}: git push --delete origin master",
                remoteProcessGpdm,
                ignoreStr="To",
            )[2]
            if remoteProcessGpdmExitCode == 1:
                repo["error"] = True
                return


if len(reposAlreadyBlasted) > 0:
    print(
        """
    The following repos have already been blasted:
    """
    )
    for repo in reposAlreadyBlasted:
        print(repo["htmlUrl"])
    print("\n")

if len(reposWithErrors) > 0:
    print(
        """
    The following repos had errors that prevented any process to run on them:
    """
    )
    for repo in reposWithErrors:
        print(f"{repo['htmlUrl']} {repo['status']}")
    print("\n")

if len(reposReadyForLocal) > 0:
    print(
        """
    The following repos are ready to update primary branch and origin locally:
    """
    )
    for repo in reposReadyForLocal:
        print(repo["htmlUrl"])
    localIsAGo = questionary.confirm("Continue?").ask()
    if not localIsAGo:
        print(
            """
    Okay! You can run the program again if you change your mind!
        """
        )
    print("\n")

if len(reposReadyForLocalMasterDelete) > 0:
    print(
        """
    The following repos could have their local branch 'master' deleted:
    """
    )
    for repo in reposReadyForLocalMasterDelete:
        print(repo["htmlUrl"])
    localMasterDeleteIsAGo = questionary.confirm("Delete? Defaults to yes.").ask()
    if localMasterDeleteIsAGo:
        print(
            """
    Okay! Local 'master' branches will be deleted!
        """
        )
    else:
        print(
            """
    Okay! You can run the program again if you change your mind!
        """
        )
    print("\n")

if len(reposReadyForRemote) > 0:
    print(
        """
    The following repos are ready to update the primary branch:
    """
    )
    for repo in reposReadyForRemote:
        print(repo["htmlUrl"])
    remoteIsAGo = questionary.confirm("Continue?").ask()
    if not remoteIsAGo:
        print(
            """
    Okay! It's a no-go for remote repos!
        """
        )
    print("\n")

if localIsAGo:
    for repo in reposReadyForLocal:
        localProcess(repo)
        if repo.get("error"):
            print(f"Error with {repo['htmlUrl']}!")
        else:
            print(f"Local process completed for {repo['htmlUrl']}")

if localMasterDeleteIsAGo:
    for repo in reposReadyForLocalMasterDelete:
        localMasterDeleteProcess(repo)
        if repo.get("error"):
            print(f"Error with {repo['htmlUrl']}!")
        else:
            print(f"Local master branch deleted for {repo['htmlUrl']}")

if remoteIsAGo:
    for repo in reposReadyForRemote:
        remoteProcess(repo)
        if repo.get("error"):
            print(f"Error with {repo['htmlUrl']}!")
        else:
            print(f"Remote process completed for {repo['htmlUrl']}")

if (
    os.path.isdir(f"{localDirectory}/master-blaster-{username}/")
    and confirmRemoveLocalDirectoriesAfter
):
    removeLocalDirectoriesProcess = Popen(
        ["rm", "-dfRv", f"./master-blaster-{username}"],
        cwd=localDirectory,
        stdout=PIPE,
        stderr=PIPE,
    )
    logging.info(f"cwd={localDirectory}: rm -dfR ./master-blaster-{username}")


# * ``` Reporting! ``` * #

if localIsAGo:
    errors = 0
    for repo in reposReadyForLocal:
        if repo.get("error"):
            errors = errors + 1
    if errors == len(reposReadyForLocal):
        print(
            f"""
    All repos ready for local process had errors!
        """
        )
    elif errors > 0:
        print(
            f"""
    {errors} errors with repos ready for the local process!
        """
        )
        print(
            f"""
    {len(reposReadyForLocal) - errors} repos completed the local process!
        """
        )
    else:
        print(
            f"""
    {len(reposReadyForLocal)} repos completed the local process!
        """
        )

if localMasterDeleteIsAGo:
    errors = 0
    for repo in reposReadyForLocalMasterDelete:
        if repo.get("error"):
            errors = errors + 1
    if errors == len(reposReadyForLocalMasterDelete):
        print(
            f"""
    All repos ready for local master branch removal had errors!
        """
        )
    elif errors > 0:
        print(
            f"""
    {errors} errors with repos ready for local master branch removal!
        """
        )
        print(
            f"""
    {len(reposReadyForLocalMasterDelete) - errors} repos completed local master branch removal!
        """
        )
    else:
        print(
            f"""
    {len(reposReadyForLocalMasterDelete)} repos completed local master branch removal!
        """
        )

if remoteIsAGo:
    errors = 0
    for repo in reposReadyForRemote:
        if repo.get("error"):
            errors = errors + 1
    if errors == len(reposReadyForRemote):
        print(
            f"""
    All repos ready for remote process had errors!
        """
        )
    elif errors > 0:
        print(
            f"""
    {errors} errors with repos ready for the remote process!
        """
        )
        print(
            f"""
    {len(reposReadyForRemote) - errors} repos completed the remote process!
        """
        )
    else:
        print(
            f"""
    {len(reposReadyForRemote)} repos completed the remote process!
        """
        )
