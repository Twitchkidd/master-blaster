#!/usr/bin/env python3

# what if you appended with Path, like
# sys.path.append(Path.cwd() / "vendor")

# Add vendor directory to module search path
parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, "vendor")

sys.path.append(vendor_dir)

import questionary
import requests


# Master Blaster - Batch Rename Primary Branches Of Code Repositories
# Copyright (C) 2020 Gareth Field - field.gareth @ gmail.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# networkActions #
# shellActions #
# auth #
# dispatch #
# logging #
# options #
# reporting #

import sys

import json
import logging

# logging #
import os
from pathlib import Path

# shellActions #
# options #
import questionary

# auth #
# options #
import requests
from subprocess import Popen, PIPE


def getActiveBranchName(path):
    # shellActions #
    # * ``` From u/merfi on SO, added a path param ``` * #
    head_dir = Path(path) / ".git" / "HEAD"
    with head_dir.open("r") as f:
        content = f.read().splitlines()
    for line in content:
        if line[0:4] == "ref:":
            return line.partition("refs/heads/")[2]


# dispatch #
# * This is meant to grab pwd if run in dev! * #
# This is needed because when you run it in dev, because the
# dev build uses pipenv, you end up in the wrong branch afterwards,
# every time after build. I don't really know why.
# This cleans up on the far side of dispatch.
# ! Testing! #
currentBranch = ""
# shellActions #
if f"{Path.home()}/Code/master-blaster" == f"{Path.cwd()}":
    currentBranch = getActiveBranchName(f"{Path.cwd()}")

# networkActions #
# This defaults to v3 of the api.
GITHUB_API = "https://api.github.com"

# reporting #
# * ``` License text! ``` * #
licenseText = """
    master-blaster: Rename primary branches of code repositories.
    Copyright (C) 2020  Gareth Field field.gareth@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
print(licenseText)

# * ``` Intro text! ``` * #
intro = """
    Welcome to master-blaster! This program batch renames primary branches for GitHub users!
    We'll go through the options before making any changes!
"""
print(intro)

# auth #
# * ``` Explanation of token thing! ``` * #
tokenExplanation = """
    Also, GitHub is deprecating password-based token generation! This is great for
    security, it just means you're going to have to go to GitHub.com and
    come back with an access token to run the program, and it's a couple of steps,
    still faster than doing each manually if you have a bunch of repos, though.
    Thank you!
"""
print(tokenExplanation)

# logging #
# * ``` Write to a new or existing log file! ``` * #
# ! Testing! #
# filemode='w' will not append to the file, it'll write over
logging.basicConfig(
    filename="info.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
# logging.basicConfig(filename='info.log',
#                     level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
# reporting #
print(
    """
    Log file to be found at ./info.log!
"""
)
# logging #
logging.info("master-blaster v1.0.5")
logging.info("Creating a log file!!")

# auth #
# * ~~~  Username gathering! ~~~ * #

# * ``` Placeholder variable for the username! ``` * #
username = ""

# * ``` Ask for username! ``` * #
usernamePrompt = """
    First, please enter your GitHub username!
"""


def usernameConfirmationPrompt(usernameInput):
    return f"Confirm username: {usernameInput}"


usernameConfirmed = False
while not usernameConfirmed:
    usernameResponse = questionary.text(usernamePrompt).ask()
    if usernameResponse == "":
        print("GitHub username blank: Please try again!")
        continue
    if len(usernameResponse) >= 40:
        print("GitHub usernames are 39 chars or less: please try again!")
        continue
    else:
        usernameConfirmationResponse = questionary.confirm(
            usernameConfirmationPrompt(usernameResponse)
        ).ask()
        if usernameConfirmationResponse == False:
            print("Thank you for retrying!")
            continue
        if usernameConfirmationResponse:
            username = usernameResponse
            # ! Testing! #
            # logging.info(f"Username: {username}")
            usernameConfirmed = True
            continue


# ! Testing ! #
username = "Twitchkidd"
# logging #
logging.info(f"Username: {username}")


# options #
# * ~~~ Set of questionary dictionary questions! ~~~ * #

# * ``` Placeholder variable for repo types!``` * #
repoTypes = ""

# * ``` What types of repos! ``` * #

# * ``` Question ``` * #
repoTypesPrompt = """
    What set of repositories do you want to update?
"""

# * ``` Choices ``` * #
repoTypesOwner = "All repositories I'm the owner of, public and private. (Collaborator/Organization repo types in development!)"
repoTypesOwnerPublic = "All repositories I'm the owner of, only public, not private."
repoTypesAll = "All repositories I'm the owner, collaborator, and/or organization member, public and private."
repoTypesAllPublic = "All repositories I'm the owner, collaborator, and/or organization member, only public, not private."
repoTypesCollaborator = (
    "All repositories I'm the owner of and/or a collaborator on, public and private."
)
repoTypesCollaboratorPublic = "All repositories I'm the owner of and/or a collaborator on, only public, not private."
repoTypesOrganization = "All repositories I'm the owner of and/or a member of the organization, public and private."
repoTypesOrganizationPublic = "All repositories I'm the owner of and/or a member of the organization, only public, not private."

# * ``` What to name the primary branches and choices! ``` * #

# * ``` Question ``` * #
namesSelectionPrompt = """
    What would you like to name your primary branches? (Default 'main'.)
"""

# * ``` Choices ``` * #
namesMain = "All primary branches renamed to 'main'."
namesCustom = "Choose name for all primary branches renamed to. "
namesPerRepo = "Choose a name for the primary branch for each repo."

questions = [
    {
        "type": "select",
        "name": "repoTypes",
        "message": repoTypesPrompt,
        "choices": [
            repoTypesOwner,
            # repoTypesOwnerPublic,
            # repoTypesAll,
            # repoTypesAllPublic,
            # repoTypesCollaborator,
            # repoTypesCollaboratorPublic,
            # repoTypesOrganization,
            # repoTypesOrganizationPublic
        ],
    },
    {
        "type": "select",
        "name": "namesSelection",
        "message": namesSelectionPrompt,
        "choices": [namesMain, namesCustom, namesPerRepo],
    },
]

# * ``` Extract the data from the set of prompts from dictionary! ``` * #
answers = questionary.prompt(questions)
# repoTypes = answers['repoTypes']
repoTypes = "All repositories I'm the owner of, public and private."
# logging #
logging.info(f"Repository types chosen: {repoTypes}")
logging.info(f"Naming selection: {answers['namesSelection']}")

# options #
# * ~~~ Custom primary branch flow! ~~~ * #

# * ``` Placeholder variable for the primary branch name! ``` * #
name = "main"

# * ``` Custom name for all branches! ``` * #
customNamePrompt = """
    What name are you choosing for primary branches?
"""

# * ``` Confirm reset to main! ``` * #
confirmResetToMainPrompt = """
    Default: use 'main' for all primary branches?
"""


def customNameConfirmPrompt(inputName):
    return f"""{inputName} for all primary branches?"""


if answers["namesSelection"] == namesCustom:
    nameConfirmed = False
    while not nameConfirmed:
        customNameResponse = questionary.text(customNamePrompt).ask()
        if customNameResponse == "":
            confirmResetToMainResponse = questionary.confirm(
                confirmResetToMainPrompt
            ).ask()
            if confirmResetToMainResponse:
                name = "main"
                nameConfirmed = True
                # logging #
                logging.info(f"Name for primary branches: {name}")
                # options #
            else:
                continue
        else:
            confirmCustomNameResponse = questionary.confirm(
                customNameConfirmPrompt(customNameResponse)
            ).ask()
            if confirmCustomNameResponse:
                name = customNameResponse
                nameConfirmed = True
                # logging #
                logging.info(f"Name for primary branches: {name}")
                # options #
                pass

# * ~~~ Interactive naming mode choice handling! ~~~ * #

# * ``` Placeholder variable for interactive naming mode! ``` * #
interactive = False

# * ``` Confirmation that interactive naming mode will happen! ``` * #
interactiveNamingConfirmationPrompt = """
    Okay! We'll name them after we fetch the set of repos!
"""

if answers["namesSelection"] == namesPerRepo:
    interactive = True
    print(interactiveNamingConfirmationPrompt)

# * ~~~ Local directory choice handling! ~~~ * #

# * ``` Local directory yay or nay! ``` * #
localDirectoriesPrompt = """
    Repositories not present locally will be cloned to a temporary folder,
    updated, the update pushed, (the default branch on GitHub.com updated,) and
    then deleted locally depending on your choice in just a moment.
    
    The program can decrease the use of bandwidth and reduce potential conflicts
    by scanning for repositories that are present locally, from home or a specified
    directory for code. Okay?
"""
localDirectories = questionary.confirm(localDirectoriesPrompt).ask()

# * ``` Placeholder variable for local directory selection! ``` * #
localDirectory = Path.home()

# * ``` Which local directory? ``` * #
localDirectoryPrompt = """
    Do you keep all of your coding projects in a certain directory? Type that in
    here to limit and speed up search. Default is home, ~/, hit enter for default.
    Example: /Users/gareth/Code
"""

# * ``` Confirm reset to home! ``` * #
confirmResetToHomePrompt = """
    Default: use '~/' for local directory search?
"""

# * ``` Placeholder variable for confirming removal of local directories after! ``` * #
confirmRemoveLocalDirectoriesAfter = False


def customLocalDirectoryConfirmPrompt(inputDir):
    return f"""{inputDir} for all primary branches?"""


# * ``` Ask which directory to use to search for local repos! ``` * #
if localDirectories:
    localDirectoryConfirmed = False
    while not localDirectoryConfirmed:
        customLocalDirectoryResponse = questionary.text(localDirectoryPrompt).ask()
        if customLocalDirectoryResponse == "":
            confirmResetToHomeResponse = questionary.confirm(
                confirmResetToHomePrompt
            ).ask()
            if confirmResetToHomeResponse:
                localDirectory = Path.home()
                localDirectoryConfirmed = True
                # ! Testing ! #
                # logging.info(f"Local directory to search: {localDirectory}")
                # options #
            else:
                continue
        else:
            # shellActions #
            if os.path.isdir(customLocalDirectoryResponse):
                # options #
                confirmCustomLocalDirectoryResponse = questionary.confirm(
                    customLocalDirectoryConfirmPrompt(customLocalDirectoryResponse)
                ).ask()
                if confirmCustomLocalDirectoryResponse:
                    localDirectory = customLocalDirectoryResponse
                    localDirectoryConfirmed = True
                    # ! Testing! #
                    # logging.info(
                    #     f"Local directory to search: {localDirectory}")
                    # options #
                    pass
            else:
                print(
                    f"Error! Directory not showing as valid: {customLocalDirectoryResponse}"
                )
                continue

# ! Testing! #
localDirectory = f"{Path.home()}/Code"
# logging #
logging.info(f"Local directory to search: {localDirectory}")

# options #
# * ``` Ask to delete cloned repos! ``` * #
confirmRemoveLocalDirectoriesAfterPrompt = """
    Remove newly cloned repositories after process complete? Defaults to yes.
"""

if localDirectories:
    confirmRemoveLocalDirectoriesAfter = questionary.confirm(
        confirmRemoveLocalDirectoriesAfterPrompt
    ).ask()
    # ! Testing! #
    # logging.info(
    #     f"Confirm remove local directories after: {confirmRemoveLocalDirectoriesAfter}")
    # options #

# ! Testing! #
confirmRemoveLocalDirectoriesAfter = True
# logging #
logging.info(
    f"Confirm remove local directories after: {confirmRemoveLocalDirectoriesAfter}"
)

# options #
# * ~~~ New Git Alias! ~~~ * #

# * ``` Placeholder variable for git alias selection! ``` * #
gitNew = True

# * ``` Prompt! ``` * #
gitNewPrompt = f"""
    Add a git alias 'git new' that initializes
    new git repos with commit as {name}? Defaults to yes.
"""

# * ``` Ask it! ``` * #
if not interactive:
    gitNew = questionary.confirm(gitNewPrompt)
    # * ``` Log the choice! ``` * #
    logging.info(f"Add git alias `git new`: {name}")

# auth #
# * ~~~ Token Time! ~~~ * #

# * ``` Placeholder variables for the token! ``` * #
token = ""

# shellActions #
# ! Testing! #
# * ``` Placeholder variables for the testing tokens! ``` * #
tokenRepoScope = ""
tokenPublicRepoScope = ""

# ! Testing! #
with open("./repo.txt", "r") as repoF:
    tokenRepoScope = repoF.read(40)

# ! Testing! #
with open("./repoPublicRepo.txt", "r") as repoPublicRepoF:
    tokenPublicRepoScope = repoPublicRepoF.read(40)

# networkActions #
if repoTypes in [
    repoTypesAll,
    repoTypesOwner,
    repoTypesCollaborator,
    repoTypesOrganization,
]:
    tokenType = "repo"
else:
    tokenType = "public repo"


def tokenPrompt(tokenTypeArg):
    # auth #
    return f"""
    -- Get a token! --

    Since password-based token generation is being deprecated,
    please get a personal access token with the correct scope(s)
    to run this program!

    To get this token, go to https://github.com, sign in,
    then go to 'Settings', then 'Developer Settings',
    then 'Personal access tokens', then 'Generate new token',
    confirm your password, name the token in the 'Note' input field,
    select the {tokenTypeArg} scope, then 'Generate Token',
    and then copy it to your clipboard.

    Please save it somewhere first in case there's an error!

    For more thorough (and visual) instructions in the GitHub docs,
    see the personal access token part here: https://bit.ly/2X0cr3j

    Paste it back here into the prompt and hit enter to continue:
    """


def getToken():
    tokenConfirmed = False
    while not tokenConfirmed:
        customTokenResponse = questionary.text(tokenPrompt(tokenType)).ask()
        if customTokenResponse == "":
            print("Please enter the token!")
            continue
        else:
            token = customTokenResponse
            tokenConfirmed = True
            continue
    # ! Testing! #
    # shellActions #
    token = tokenRepoScope
    # # token = "fermf"
    # auth #
    return token


# networkActions #
# * ``` Constructing the url! ``` * #


def constructReposUrl():
    return f"{GITHUB_API}/user/repos"


# * ``` Construct the headers! ``` * #


def constructHeaders(token):
    headers = {"Authorization": "token " + token}
    return headers


# * ``` Custruct the parameters! ``` * #


def constructReposParams():
    params = {}
    if repoTypes == repoTypesAll:
        params = {
            "per_page": "1000",
        }
    if repoTypes == repoTypesAllPublic:
        params = {"per_page": "1000", "visibility": "public"}
    # if repoTypes == repoTypesOwner:
    if repoTypes == "All repositories I'm the owner of, public and private.":
        params = {"per_page": "1000", "type": "owner"}
    if repoTypes == repoTypesOwnerPublic:
        params = {"per_page": "1000", "visibility": "public", "type": "owner"}
    if repoTypes == repoTypesCollaborator:
        params = {"per_page": "1000", "type": "owner,collaborator"}
    if repoTypes == repoTypesCollaboratorPublic:
        params = {
            "per_page": "1000",
            "visibility": "public",
            "type": "owner,collaborator",
        }
    if repoTypes == repoTypesOrganization:
        params = {"per_page": "1000", "type": "owner,collaborator,organization_member"}
    if repoTypes == repoTypesOrganizationPublic:
        params = {
            "per_page": "1000",
            "visibility": "public",
            "type": "owner,collaborator,organization_member",
        }
    return params


# options #
# * ``` Placeholder variable for the total set of repos! ``` * #
repos = []

# auth #
# dispatch #
# options #
# networkActions #
# * ``` Ask for the token until the response comes back okay, then extract the data from the API call! ``` * #
reposResponseConfirmed = False
while not reposResponseConfirmed:
    token = getToken()
    url = constructReposUrl()
    params = constructReposParams()
    headers = constructHeaders(token)
    print("Checking for repos ...")
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

# options #
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
                    # logging #
                    logging.info(f"Primary branch name for {repo['htmlUrl']}: {name}")
                    # options #
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
                    # logging #
                    logging.info(
                        f"Primary branch name for {repo['htmlUrl']}: {repoNameResponse}"
                    )
                    # options #
                    continue
                else:
                    pass

# * ~~~ Take all these repos and test them against what the name is supposed to be! ~~~ * #

# networkActions #
# * ``` Construct the url! ``` * #


def constructBranchesUrl(repo, which):
    return f"{GITHUB_API}/repos/{repo['owner-login']}/{repo['name']}/branches/{which}"


# dispatch #
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

# shellActions #
# * ``` Check git config file for remote url! ``` * #


def getLocalRepoUrl(configFile):
    url = ""
    for line in configFile:
        if line.find("url =") != -1:
            remoteOriginUrlStart = line.find("url =")
            url = line[remoteOriginUrlStart + 6 : -1]
            return url


# shellActions #
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
    """This function logs the first argument, *RUNS* the code, capturing
    stdout and stderr, logging those, possibly checks against the third
    argument, though not the fourth (?) and returns a thruple of stdout,
    stderr, and either a 0 for success or a 1 for error."""
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

# * Add the `git new` alias! * #


def runGitNew():
    # shellActions #
    gitNewGcg = Popen(
        [
            "git",
            "config",
            "--global",
            "alias.new",
            f"!git init && git symbolic-ref HEAD refs/heads/{name}",
        ],
        stdout=PIPE,
        stderr=PIPE,
    )
    # logging #
    gitNewGcgExitCode = processLogger(
        f"git config --global alias.new '!git init && git symbolic-ref HEAD refs/heads/{name}'",
        gitNewGcg,
    )[2]
    # reporting #
    if gitNewGcgExitCode == 0:
        print(f"Git alias git new: initalize git repo with HEAD ref refs/heads/{name}")
    else:
        print("Git alias add failed, see log file.")


# dispatch #
if gitNew:
    runGitNew()


# reporting #
# * ``` Denoument! ``` * #

print("Thank you for using master-blaster!\n")
print("Check the log file at ./info.log for details!")

# shellActions#
# ! Testing! #
if len(currentBranch) > 0:
    Popen(["git", "checkout", f"{currentBranch}"], stdout=PIPE, stderr=PIPE)

# // sys.exit()
