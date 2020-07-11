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

import json
import logging
import os
from pathlib import Path
import questionary
import requests
from subprocess import Popen, PIPE
import sys

# // ! Testing! #
# // * ``` From u/merfi on SO! ``` * #


# def get_active_branch_name():

#     head_dir = Path(".") / ".git" / "HEAD"
#     with head_dir.open("r") as f:
#         content = f.read().splitlines()

#     for line in content:
#         if line[0:4] == "ref:":
#             return line.partition("refs/heads/")[2]


# currentBranch = ""
# if(f"{Path.home()}/Code/master-blaster" == f"{Path.cwd()}"):
#     currentBranch = get_active_branch_name()

# This defaults to v3 of the api.
GITHUB_API = "https://api.github.com"

# * ``` License text! ``` * #
licenseText = """
    master-blaster  Copyright (C) 2020  Gareth Field
    This program comes with ABSOLUTELY NO WARRANTY;
    This is free software, and you are welcome to redistribute it
    under certain conditions;
"""
# licenseText = """
#     master-blaster  Copyright (C) 2020  Gareth Field
#     This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
#     This is free software, and you are welcome to redistribute it
#     under certain conditions; type `show c' for details.
# """
print(licenseText)
# print("Working on `show w' and `show c', actually! It's GNU public 3+! No closed versions!")

# * ``` Intro text! ``` * #
intro = """
    Welcome to master-blaster! This program batch renames primary branches for GitHub users!
    We'll go through the options before making any changes!
"""
print(intro)

# * ``` Explanation of token thing! ``` * #
tokenExplanation = """
    GitHub is deprecating password-based token generation! This is great for
    security, it just means you're going to have to go to GitHub.com and
    come back with an access token to make this program work.
"""
# tokenExplanation = """
#     GitHub is deprecating password-based token generation! This is great for
#     security, it just means you're going to have to go to GitHub.com and
#     come back with an access token to make this program work.

#     The next question will determine whether the program needs a token with the more
#     general `repo` scope or the more limited `public_repo` scope, and there will
#     be instructions for what to do at GitHub.com when we're ready to go here. This
#     program can be run again for further and any future repos.
# """
print(tokenExplanation)

# * ``` Write to a new or existing log file! ``` * #
# // ! Testing! #
# # filemode='w' will not append to the file, it'll write over
# logging.basicConfig(filename='info.log', filemode='w',
#                     level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logging.basicConfig(filename='info.log',
                    level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
print("""
    Log file to be found at ./info.log!
""")
logging.info("Creating a log file!!")

# * ~~~  Username gathering! ~~~ * #

# * ``` Placeholder variable for the username! ``` * #
username = ""

# * ``` Ask for username! ``` * #
usernamePrompt = """
    Please enter your GitHub username!
"""


def usernameConfirmationPrompt(usernameInput):
    return f"GitHub username: {usernameInput}?"


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
            usernameConfirmationPrompt(usernameResponse)).ask()
        if usernameConfirmationResponse == False:
            print("Thank you for retrying!")
            continue
        if usernameConfirmationResponse:
            username = usernameResponse
            # // ! Testing! #
            logging.info(f"Username: {username}")
            usernameConfirmed = True
            continue


# // ! Testing ! #
# username = "Twitchkidd"
# logging.info(f"Username: {username}")

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
repoTypesCollaborator = "All repositories I'm the owner of and/or a collaborator on, public and private."
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
        ]
    },
    {
        "type": "select",
        "name": "namesSelection",
        "message": namesSelectionPrompt,
        "choices": [
            namesMain,
            namesCustom,
            namesPerRepo
        ]
    }
]

# * ``` Extract the data from the set of prompts from dictionary! ``` * #
answers = questionary.prompt(questions)
repoTypes = answers['repoTypes']
logging.info(f"Repository types chosen: {repoTypes}")
logging.info(f"Naming selection: {answers['namesSelection']}")

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
    return f'''{inputName} for all primary branches?'''


if answers['namesSelection'] == namesCustom:
    nameConfirmed = False
    while not nameConfirmed:
        customNameResponse = questionary.text(customNamePrompt).ask()
        if customNameResponse == "":
            confirmResetToMainResponse = questionary.confirm(
                confirmResetToMainPrompt).ask()
            if confirmResetToMainResponse:
                name = "main"
                nameConfirmed = True
                logging.info(f"Name for primary branches: {name}")
            else:
                continue
        else:
            confirmCustomNameResponse = questionary.confirm(
                customNameConfirmPrompt(customNameResponse)).ask()
            if confirmCustomNameResponse:
                name = customNameResponse
                nameConfirmed = True
                logging.info(f"Name for primary branches: {name}")
                pass

# * ~~~ Interactive naming mode choice handling! ~~~ * #

# * ``` Placeholder variable for interactive naming mode! ``` * #
interactive = False

# * ``` Confirmation that interactive naming mode will happen! ``` * #
interactiveNamingConfirmationPrompt = """
    Okay! We'll name them after we fetch the set of repos!
"""

if answers['namesSelection'] == namesPerRepo:
    interactive = True
    print(interactiveNamingConfirmationPrompt)

# * ~~~ Local directory choice handling! ~~~ * #

# * ``` Local directory yay or nay! ``` * #
localDirectoriesPrompt = """
    Repositories not present locally will be cloned to a temporary folder,
    updated, the update pushed, (the default branch on GitHub.com updated,) and
    then deleted locally depending on your choice in two questions. This can
    decrease the use of bandwidth and reduce potential conflicts by scanning for
    repositories that are present locally. Is this okay?
"""
localDirectories = questionary.confirm(localDirectoriesPrompt).ask()

# * ``` Placeholder variable for local directory selection! ``` * #
localDirectory = Path.home()

# * ``` Which local directory? ``` * #
localDirectoryPrompt = """
    Do you keep all of your projects in a certain directory? Type that in here
    to limit and speed up search. Default is ~/, hit enter for default.
    Example: /Users/gareth/Code
"""

# * ``` Confirm reset to home! ``` * #
confirmResetToHomePrompt = """
    Default: use '~/' for local directory search?
"""

# * ``` Placeholder variable for confirming removal of local directories after! ``` * #
confirmRemoveLocalDirectoriesAfter = False


def customLocalDirectoryConfirmPrompt(inputDir):
    return f'''{inputDir} for all primary branches?'''


# * ``` Ask which directory to use to search for local repos! ``` * #
if localDirectories:
    localDirectoryConfirmed = False
    while not localDirectoryConfirmed:
        customLocalDirectoryResponse = questionary.text(
            localDirectoryPrompt).ask()
        if customLocalDirectoryResponse == "":
            confirmResetToHomeResponse = questionary.confirm(
                confirmResetToHomePrompt).ask()
            if confirmResetToHomeResponse:
                localDirectory = Path.home()
                localDirectoryConfirmed = True
                # // ! Testing! #
                logging.info(f"Local directory to search: {localDirectory}")
            else:
                continue
        else:
            if os.path.isdir(customLocalDirectoryResponse):
                confirmCustomLocalDirectoryResponse = questionary.confirm(
                    customLocalDirectoryConfirmPrompt(customLocalDirectoryResponse)).ask()
                if confirmCustomLocalDirectoryResponse:
                    localDirectory = customLocalDirectoryResponse
                    localDirectoryConfirmed = True
                    # // ! Testing! #
                    logging.info(
                        f"Local directory to search: {localDirectory}")
                    pass
            else:
                print(
                    f"Error! Directory not showing as valid: {customLocalDirectoryResponse}")
                continue

# // ! Testing! #
# localDirectory = f"{Path.home()}/Code"
# logging.info(f"Local directory to search: {localDirectory}")

# * ``` Ask to delete cloned repos! ``` * #
confirmRemoveLocalDirectoriesAfterPrompt = """
    Remove newly cloned repositories after process complete? Defaults to yes.
"""

if localDirectories:
    confirmRemoveLocalDirectoriesAfter = questionary.confirm(
        confirmRemoveLocalDirectoriesAfterPrompt).ask()
    # // ! Testing! #
    logging.info(
        f"Confirm remove local directories after: {confirmRemoveLocalDirectoriesAfter}")

# // ! Testing! #
# confirmRemoveLocalDirectoriesAfter = True
# logging.info(
#     f"Confirm remove local directories after: {confirmRemoveLocalDirectoriesAfter}")

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


# * ~~~ Token Time! ~~~ * #

# * ``` Placeholder variables for the token! ``` * #
token = ""

# // ! ``` Placeholder variables for the testing tokens! ``` ! #
# // ! Testing! #
# tokenRepoScope = ""
# tokenPublicRepoScope = ""

# // ! Testing! #
# with open("./repo.txt", 'r') as repoF:
#     tokenRepoScope = repoF.read(40)

# // ! Testing! #
# with open("./repoPublicRepo.txt", 'r') as repoPublicRepoF:
#     tokenPublicRepoScope = repoPublicRepoF.read(40)

if repoTypes in [repoTypesAll, repoTypesOwner, repoTypesCollaborator, repoTypesOrganization]:
    tokenType = "repo"
else:
    tokenType = "public repo"


def tokenPrompt(tokenTypeArg):
    return f"""
    -- Get a token! --
    Since password-based token generation is being deprecated,
    please get a personal access token with the correct scope(s)
    in order to run this program.
    To get this token, go to https://github.com, sign in,
    then go to 'Settings', then 'Developer Settings',
    then 'Personal access tokens', then 'Generate new token',
    confirm your password, name the token in the 'Note' input field,
    and select the {tokenTypeArg} scope, then 'Generate Token',
    then copy it to your clipboard,
    please save it first in case there's an error,
    then paste it back here into the prompt,
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
    # // ! Testing! #
    # # token = tokenRepoScope
    # # token = "fermf"
    return token


# * ``` Constructing the url! ``` * #


def constructReposUrl():
    return f"{GITHUB_API}/user/repos"

# * ``` Construct the headers! ``` * #


def constructHeaders(token):
    headers = {"Authorization": 'token ' + token}
    return headers

# * ``` Custruct the parameters! ``` * #


def constructReposParams():
    params = {}
    if repoTypes == repoTypesAll:
        params = {"per_page": "1000", }
    if repoTypes == repoTypesAllPublic:
        params = {"per_page": "1000", "visibility": "public"}
    if repoTypes == repoTypesOwner:
        params = {"per_page": "1000", "type": "owner"}
    if repoTypes == repoTypesOwnerPublic:
        params = {"per_page": "1000", "visibility": "public", "type": "owner"}
    if repoTypes == repoTypesCollaborator:
        params = {"per_page": "1000", "type": "owner,collaborator"}
    if repoTypes == repoTypesCollaboratorPublic:
        params = {"per_page": "1000", "visibility": "public",
                  "type": "owner,collaborator"}
    if repoTypes == repoTypesOrganization:
        params = {"per_page": "1000",
                  "type": "owner,collaborator,organization_member"}
    if repoTypes == repoTypesOrganizationPublic:
        params = {"per_page": "1000", "visibility": "public",
                  "type": "owner,collaborator,organization_member"}
    return params


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
    reposResponse = requests.get(url, params=params, headers=headers)
    # Bad token returns a 401! #
    if reposResponse.status_code >= 400:
        logging.warning(f"Response status: {reposResponse.status_code}")
        print(
            f"Network error! Possibly the token! Try again please! If this is not your GitHub username, please restart the program: {username}")
        continue
    else:
        print("Repos received!")
        reposResponseConfirmed = True
        for repository in reposResponse.json():
            repos.append(
                {"defaultBranch": repository['default_branch'], "htmlUrl": repository['html_url'], "name": repository['name'], "owner-login": f"{repository['owner']['login']}", "primaryBranchName": name})
        pass


# * If they wanted to name each primary branch, do so now! * #
if interactive:
    print("""
        Interactive naming mode!
    """)
    for repo in repos:
        primaryBranchNameConfirmed = False
        while not primaryBranchNameConfirmed:
            repoNameResponse = questionary.text(
                f"Primary branch name for {repo['htmlUrl']}?").ask()
            if repoNameResponse == "":
                defaultNameResponse = questionary.confirm(
                    f"Default primary branch name {name} for {repo['htmlUrl']}?")
                if defaultNameResponse:
                    logging.info(
                        f"Primary branch name for {repo['htmlUrl']}: {name}")
                    primaryBranchNameConfirmed = True
                    continue
                else:
                    continue
            else:
                customRepoNameConfirmed = questionary.confirm(
                    f"{repoNameResponse} for {repo['htmlUrl']}?")
                if customRepoNameConfirmed:
                    primaryBranchNameConfirmed = True
                    repo['primaryBranchName'] = repoNameResponse
                    logging.info(
                        f"Primary branch name for {repo['htmlUrl']}: {repoNameResponse}")
                    continue
                else:
                    pass


# * ~~~ Take all these repos and test them against what the name is supposed to be! ~~~ * #

# * ``` Construct the url! ``` * #
def constructBranchesUrl(repo, which):
    return f"{GITHUB_API}/repos/{repo['owner-login']}/{repo['name']}/branches/{which}"


# * ``` Check each remote to see if they have master branches or branches with the name already! ``` * #
for repo in repos:
    primaryBranchUrl = constructBranchesUrl(repo, repo['primaryBranchName'])
    masterBranchUrl = constructBranchesUrl(repo, "master")
    headers = constructHeaders(token)
    print(f"Checking branches for {repo['htmlUrl']}.")
    primaryBranchResponse = requests.get(primaryBranchUrl, headers=headers)
    masterBranchResponse = requests.get(masterBranchUrl, headers=headers)
    if primaryBranchResponse.json().get('message'):
        repo['hasPrimaryBranchName'] = False
    if masterBranchResponse.json().get('message'):
        repo['hasMasterBranch'] = False
    if primaryBranchResponse.json().get('name'):
        repo['hasPrimaryBranchName'] = True
    if masterBranchResponse.json().get('name'):
        repo['hasMasterBranch'] = True


# * ~~~ If they wanted to use local clones, look for them! ~~~ * #

# * ``` Placeholder variable for the set of local repos! ``` * #
localRepos = []


# * ``` Check got config file for remote url! ``` * #
def getLocalRepoUrl(configFile):
    url = ""
    for line in configFile:
        if line.find('url =') != -1:
            remoteOriginUrlStart = line.find('url =')
            url = line[remoteOriginUrlStart + 6:-1]
            return url


# * ``` Find all local repos that share a name with the repos to change! (Url is test for owner!) ``` * #
if localDirectories:
    repoNames = [repo['name'] for repo in repos]
    for root, subdirs, files in os.walk(f"{localDirectory}"):
        for subdir in subdirs:
            if any(subdir == repoName for repoName in repoNames):
                try:
                    with open(f"{root}/{subdir}/.git/config", "r") as configFile:
                        localRepos.append(
                            {"url": getLocalRepoUrl(configFile), "path": f"{root}/{subdir}"})
                except Exception as err:
                    # print(f"Exception: {err}")
                    pass

# * ~~~ Change the branches! ~~~ * #

# * ``` The set of local repo origin urls! ``` * #
localRepoUrls = [localRepo['url'] for localRepo in localRepos]

# * ``` Placeholder variables for groups of checked repos! ``` * #
reposAlreadyBlasted = []
reposWithErrors = []
reposReadyForLocal = []
reposReadyForLocalMasterDelete = []
reposReadyForRemote = []

# * ``` Take in the state of the branch names and defaults and categorize them! ``` * #


def check(repo):
    if repo['hasMasterBranch'] and repo['hasPrimaryBranchName']:
        repo['status'] = "error: remote has both master branch and new primary branch name"
        reposWithErrors.append(repo)
        return None
    if not repo['hasMasterBranch'] and not repo['hasPrimaryBranchName']:
        repo['status'] = "error: remote has neither master nor new primary branch name"
        reposWithErrors.append(repo)
        return None
    if repo.get('localHasPrimaryBranchName') != None:
        if not repo['hasMasterBranch'] and repo['hasPrimaryBranchName'] and repo['defaultBranch'] == repo['primaryBranchName'] and not repo['localHasMaster'] and repo['localHasPrimaryBranchName']:
            repo['status'] = "already blasted"
            reposAlreadyBlasted.append(repo)
            return None
        if not repo['hasMasterBranch'] and repo['hasPrimaryBranchName'] and repo['defaultBranch'] == repo['primaryBranchName'] and repo['localHasMaster'] and repo['localHasPrimaryBranchName']:
            repo['status'] = "candidate to delete local master"
            reposReadyForLocalMasterDelete.append(repo)
            return None
        if repo['localHasMaster'] and not repo['localHasPrimaryBranchName']:
            if not repo['hasMasterBranch'] and repo['hasPrimaryBranchName'] and repo['defaultBranch'] == repo['primaryBranchName']:
                repo['status'] = "candidate for local process"
                reposReadyForLocal.append(repo)
                return None
            if repo['hasMasterBranch'] and not repo['hasPrimaryBranchName'] and repo['defaultBranch'] == "master":
                repo['status'] = "candidate for remote process"
                reposReadyForRemote.append(repo)
                return None
        repo['status'] = f"error: {repo}"
        reposWithErrors.append(repo)
        return None
    else:
        if not repo['hasMasterBranch'] and repo['hasPrimaryBranchName'] and repo['defaultBranch'] == repo['primaryBranchName']:
            repo['status'] = "already blasted"
            reposAlreadyBlasted.append(repo)
            return None
        if repo['hasMasterBranch'] and not repo['hasPrimaryBranchName'] and repo['defaultBranch'] == "master":
            repo['status'] = "candidate for remote process"
            reposReadyForRemote.append(repo)
            return None
    repo['status'] = f"error: {repo}"
    reposWithErrors.append(repo)
    return None


# * ``` Check all the repos! (And prepare any locals for the check!) ``` * #
if localDirectories:
    print("Checking repos ...")
    for repo in repos:
        if f"{repo['htmlUrl']}.git" in localRepoUrls:
            localPath = ""
            for localRepo in localRepos:
                if localRepo['url'] == f"{repo['htmlUrl']}.git":
                    localPath = localRepo['path']
            localBranchInfoGitBranch = Popen(
                ["git", "branch"], cwd=localPath,  stdout=PIPE, stderr=PIPE)
            logging.info(f"cwd={localPath}: git branch")
            localBranchInfoGitBranchStdout, localBranchInfoGitBranchStderr = localBranchInfoGitBranch.communicate()
            logging.info(
                f"localBranchInfoGitBranchStdout: {localBranchInfoGitBranchStdout}")
            if len(localBranchInfoGitBranchStderr) > 0:
                logging.warning(
                    f"localBranchInfoGitBranchStderr: {localBranchInfoGitBranchStderr}")
            repo['localHasMaster'] = "master" in f"{localBranchInfoGitBranchStdout}"
            repo['localHasPrimaryBranchName'] = repo[
                'primaryBranchName'] in f"{localBranchInfoGitBranchStdout}"
            check(repo)
        else:
            check(repo)
else:
    print("Checking repos ...")
    for repo in repos:
        check(repo)

# * ``` Placeholder variable for local and remote processes being a go! ``` * #
localIsAGo = False
localMasterDeleteIsANoGo = True
remoteIsAGo = False


# * ``` Update local repo that still has master to sync with remote that already has the chosen name! ``` * #
def localProcess(repo):
    for localRepo in localRepos:
        if f"{repo['htmlUrl']}.git" == localRepo['url']:
            localProcessGcm = Popen(["git", "checkout", "master"], cwd=localRepo['path'],
                                    stdout=PIPE, stderr=PIPE)
            logging.info(f"cwd={localRepo['path']}: git checkout master")
            localProcessGcmStdout, localProcessGcmStderr = localProcessGcm.communicate()
            if len(localProcessGcmStdout) > 0:
                logging.info(localProcessGcmStdout)
            if len(localProcessGcmStderr) > 0:
                logging.warning(localProcessGcmStderr)
                logging.info("You may be able to ignore the above warning.")
            localProcessGbm = Popen(["git", "branch", "-m", "master", repo['primaryBranchName']], cwd=localRepo['path'],
                                    stdout=PIPE, stderr=PIPE)
            logging.info(
                f"cwd={localRepo['path']}: git branch -m master {repo['primaryBranchName']}")
            localProcessGbmStdout, localProcessGbmStderr = localProcessGbm.communicate()
            if len(localProcessGbmStdout) > 0:
                logging.info(localProcessGbmStdout)
            if len(localProcessGbmStderr) > 0:
                logging.warning(localProcessGbmStderr)
                repo['error'] = True
                return
            localProcessGf = Popen(["git", "fetch"], cwd=localRepo['path'],
                                   stdout=PIPE, stderr=PIPE)
            logging.info(f"cwd={localRepo['path']}: git fetch")
            localProcessGfStdout, localProcessGfStderr = localProcessGf.communicate()
            if len(localProcessGfStdout) > 0:
                logging.info(localProcessGfStdout)
            if len(localProcessGfStderr) > 0:
                logging.warning(localProcessGfStderr)
                logging.info("You may be able to ignore the above warning.")
            localProcessGbuu = Popen(["git", "branch", "--unset-upstream"], cwd=localRepo['path'],
                                     stdout=PIPE, stderr=PIPE)
            logging.info(
                f"cwd={localRepo['path']}: git branch --unset-upstream")
            localProcessGbuuStdout, localProcessGbuuStderr = localProcessGbuu.communicate()
            if len(localProcessGbuuStdout) > 0:
                logging.info(localProcessGbuuStdout)
            if len(localProcessGbuuStderr) > 0:
                logging.warning(localProcessGbuuStderr)
                repo['error'] = True
                return
            localProcessGbuo = Popen(["git", "branch", "-u", f"origin/{repo['primaryBranchName']}"], cwd=localRepo['path'],
                                     stdout=PIPE, stderr=PIPE)
            logging.info(
                f"cwd={localRepo['path']}: git branch -u origin/{repo['primaryBranchName']}")
            localProcessGbuoStdout, localProcessGbuoStderr = localProcessGbuo.communicate()
            if len(localProcessGbuoStdout) > 0:
                logging.info(localProcessGbuoStdout)
            if len(localProcessGbuoStderr) > 0:
                logging.warning(localProcessGbuoStderr)
                repo['error'] = True
                return
            localProcessGsro = Popen(["git", "symbolic-ref", "refs/remotes/origin/HEAD",
                                      f"refs/remotes/origin/{repo['primaryBranchName']}"], cwd=localRepo['path'],  stdout=PIPE, stderr=PIPE)
            logging.info(
                f"cwd={localRepo['path']}: git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/{repo['primaryBranchName']}")
            localProcessGsroStdout, localProcessGsroStderr = localProcessGsro.communicate()
            if len(localProcessGsroStdout) > 0:
                logging.info(localProcessGsroStdout)
            if len(localProcessGsroStderr) > 0:
                logging.warning(localProcessGsroStderr)
                repo['error'] = True
                return


# * ``` Delete stray master branch! ``` * #

def localMasterDeleteProcess(repo):
    for localRepo in localRepos:
        if f"{repo['htmlUrl']}.git" == localRepo['url']:
            localMasterDeleteProcessBranchD = Popen(
                ["git", "branch", "-d", "master"], cwd=localRepo['path'],  stdout=PIPE, stderr=PIPE)
            logging.info(f"cwd={localRepo['path']}: git branch -d master")
            localMasterDeleteProcessBranchDStdout, localMasterDeleteProcessBranchDStderr = localMasterDeleteProcessBranchD.communicate()
            if len(localMasterDeleteProcessBranchDStdout) > 0:
                logging.info(localMasterDeleteProcessBranchDStdout)
            if len(localMasterDeleteProcessBranchDStderr) > 0:
                logging.warning(localMasterDeleteProcessBranchDStderr)
                repo['error'] = True
                return


# * ``` Update remote repo that still has master! ``` * #

def constructPatchDefaultUrl(repo):
    return f"{GITHUB_API}/repos/{repo['owner-login']}/{repo['name']}"


# * ``` Placeholder variable for failing to make temp dir! ``` * #
failedToMakeTempDir = False


def remoteProcess(repo):
    if localDirectories:
        if f"{repo['htmlUrl']}.git" in localRepoUrls:
            for localRepo in localRepos:
                if f"{repo['htmlUrl']}.git" == localRepo['url']:
                    remoteProcessLocalRepoGbm = Popen(["git", "branch", "-m", "master", repo['primaryBranchName']], cwd=localRepo['path'],
                                                      stdout=PIPE, stderr=PIPE)
                    logging.info(
                        f"cwd={localRepo['path']}: git branch -m master {repo['primaryBranchName']}")
                    remoteProcessLocalRepoGbmStdout, remoteProcessLocalRepoGbmStderr = remoteProcessLocalRepoGbm.communicate()
                    if len(remoteProcessLocalRepoGbmStdout) > 0:
                        logging.info(remoteProcessLocalRepoGbmStdout)
                    if len(remoteProcessLocalRepoGbmStderr) > 0:
                        logging.warning(remoteProcessLocalRepoGbmStderr)
                        repo['error'] = True
                        return
                    remoteProcessLocalRepoGpuo = Popen(["git", "push", "-u", "origin", repo['primaryBranchName']], cwd=localRepo['path'],
                                                       stdout=PIPE, stderr=PIPE)
                    logging.info(
                        f"cwd={localRepo['path']}: git push -u origin {repo['primaryBranchName']}")
                    remoteProcessLocalRepoGpuoStdout, remoteProcessLocalRepoGpuoStderr = remoteProcessLocalRepoGpuo.communicate()
                    if len(remoteProcessLocalRepoGpuoStdout) > 0:
                        logging.info(remoteProcessLocalRepoGpuoStdout)
                    if len(remoteProcessLocalRepoGpuoStderr) > 0:
                        logging.warning(remoteProcessLocalRepoGpuoStderr)
                        logging.info(
                            "You may be able to ignore the above warning.")
                    url = constructPatchDefaultUrl(repo)
                    data = json.dumps(
                        {"default_branch": f"{repo['primaryBranchName']}"})
                    headers = constructHeaders(token)
                    patchDefaultResponse = requests.patch(
                        url, data=data, headers=headers)
                    if patchDefaultResponse.status_code >= 400:
                        logging.warning(
                            f"{repo['htmlUrl']} default branch change failed, response status: {patchDefaultResponse.status_code}")
                        repo['error'] = True
                        return
                    else:
                        logging.info(
                            f"Default branch for {repo['htmlUrl']} updated to {repo['primaryBranchName']}.")
                        remoteProcessLocalRepoGpdm = Popen(
                            ["git", "push", "--delete", "origin", "master"], cwd=f"{localRepo['path']}", stdout=PIPE, stderr=PIPE)
                        logging.info(
                            f"cwd={localRepo['path']}: git push --delete origin master")
                        remoteProcessLocalRepoGpdmStdout, remoteProcessLocalRepoGpdmStderr = remoteProcessLocalRepoGpdm.communicate()
                        if len(remoteProcessLocalRepoGpdmStdout) > 0:
                            logging.info(remoteProcessLocalRepoGpdmStdout)
                        if len(remoteProcessLocalRepoGpdmStderr) > 0:
                            logging.warning(remoteProcessLocalRepoGpdmStderr)
                            logging.info(
                                "You may be able to ignore the above warning.")
        else:
            if not os.path.isdir(f"{localDirectory}/master-blaster-{username}/"):
                remoteProcessRemoteRepoMkdir = Popen(
                    ["mkdir", "-pv", f"{localDirectory}/master-blaster-{username}/"], cwd=localDirectory,  stdout=PIPE, stderr=PIPE)
                logging.info(
                    f"cwd={localDirectory}: mkdir -pv {localDirectory}/master-blaster-{username}/")
                remoteProcessRemoteRepoMkdirStdout, remoteProcessRemoteRepoMkdirStderr = remoteProcessRemoteRepoMkdir.communicate()
                if len(remoteProcessRemoteRepoMkdirStdout) > 0:
                    logging.info(remoteProcessRemoteRepoMkdirStdout)
                if len(remoteProcessRemoteRepoMkdirStderr) > 0:
                    logging.warning(remoteProcessRemoteRepoMkdirStderr)
                    failedToMakeTempDir = True
                    return
            remoteProcessRemoteRepoGcl = Popen(["git", "clone", f"{repo['htmlUrl']}.git", f"./{repo['owner-login']}/{repo['name']}"], cwd=f"{localDirectory}/master-blaster-{username}/",
                                               stdout=PIPE, stderr=PIPE)
            logging.info(
                f"cwd={localDirectory}/master-blaster-{username}/: git clone {repo['htmlUrl']}.git ./{repo['owner-login']}/{repo['name']}")
            remoteProcessRemoteRepoGclStdout, remoteProcessRemoteRepoGclStderr = remoteProcessRemoteRepoGcl.communicate()
            if len(remoteProcessRemoteRepoGclStdout) > 0:
                logging.info(remoteProcessRemoteRepoGclStdout)
            if len(remoteProcessRemoteRepoGclStderr) > 0:
                logging.warning(remoteProcessRemoteRepoGclStderr)
                logging.info("You may be able to ignore the above warning.")
            remoteProcessRemoteRepoGbm = Popen(["git", "branch", "-m", "master", repo['primaryBranchName']], cwd=f"{localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}",
                                               stdout=PIPE, stderr=PIPE)
            logging.info(
                f"cwd={localDirectory}/master-blaster-{username}/{repo['owner-login']}: git branch -m master {repo['primaryBranchName']}")
            remoteProcessRemoteRepoGbmStdout, remoteProcessRemoteRepoGbmStderr = remoteProcessRemoteRepoGbm.communicate()
            if len(remoteProcessRemoteRepoGbmStdout) > 0:
                logging.info(remoteProcessRemoteRepoGbmStdout)
            if len(remoteProcessRemoteRepoGbmStderr) > 0:
                logging.warning(remoteProcessRemoteRepoGbmStderr)
                repo['error'] = True
                return
            remoteProcessRemoteRepoGpuo = Popen(["git", "push", "-u", "origin", repo['primaryBranchName']], cwd=f"{localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}",
                                                stdout=PIPE, stderr=PIPE)
            logging.info(
                f"cwd={localDirectory}/master-blaster-{username}/{repo['owner-login']}: git push -u origin {repo['primaryBranchName']}")
            remoteProcessRemoteRepoGpuoStdout, remoteProcessRemoteRepoGpuoStderr = remoteProcessRemoteRepoGpuo.communicate()
            if len(remoteProcessRemoteRepoGpuoStdout) > 0:
                logging.info(remoteProcessRemoteRepoGpuoStdout)
            if len(remoteProcessRemoteRepoGpuoStderr) > 0:
                logging.warning(remoteProcessRemoteRepoGpuoStderr)
                logging.info("You may be able to ignore the above warning.")
            url = constructPatchDefaultUrl(repo)
            data = json.dumps(
                {"default_branch": f"{repo['primaryBranchName']}"})
            headers = constructHeaders(token)
            patchDefaultResponse = requests.patch(
                url, data=data, headers=headers)
            if patchDefaultResponse.status_code >= 400:
                logging.warning(
                    f"{repo['htmlUrl']} default branch change failed, response status: {patchDefaultResponse.status_code}")
                repo['error'] = True
                return
            else:
                logging.info(
                    f"Default branch for {repo['htmlUrl']} updated to {repo['primaryBranchName']}.")
                remoteProcessGpdm = Popen(
                    ["git", "push", "--delete", "origin", "master"], cwd=f"{localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}", stdout=PIPE, stderr=PIPE)
                logging.info(
                    f"cwd={localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}: git push --delete origin master")
                remoteProcessGpdmStdout, remoteProcessGpdmStderr = remoteProcessGpdm.communicate()
                if len(remoteProcessGpdmStdout) > 0:
                    logging.info(remoteProcessGpdmStdout)
                if len(remoteProcessGpdmStderr) > 0:
                    logging.warning(remoteProcessGpdmStderr)
                    logging.info(
                        "You may be able to ignore the above warning.")
    else:
        if not os.path.isdir(f"{localDirectory}/master-blaster-{username}/"):
            remoteProcessRemoteRepoMkdir = Popen(
                ["mkdir", "-pv", f"{localDirectory}/master-blaster-{username}/"], cwd=localDirectory,  stdout=PIPE, stderr=PIPE)
            logging.info(
                f"cwd={localDirectory}: mkdir -pv {localDirectory}/master-blaster-{username}/")
            remoteProcessRemoteRepoMkdirStdout, remoteProcessRemoteRepoMkdirStderr = remoteProcessRemoteRepoMkdir.communicate()
            if len(remoteProcessRemoteRepoMkdirStdout) > 0:
                logging.info(remoteProcessRemoteRepoMkdirStdout)
            if len(remoteProcessRemoteRepoMkdirStderr) > 0:
                logging.warning(remoteProcessRemoteRepoMkdirStderr)
                repo['error'] = True
                return
        remoteProcessRemoteRepoGcl = Popen(["git", "clone", f"{repo['htmlUrl']}.git", f"./{repo['owner-login']}/{repo['name']}"], cwd=f"{localDirectory}/master-blaster-{username}",
                                           stdout=PIPE, stderr=PIPE)
        logging.info(
            f"cwd={localDirectory}/master-blaster-{username}: git clone {repo['htmlUrl']}.git ./{repo['owner-login']}/{repo['name']}")
        remoteProcessRemoteRepoGclStdout, remoteProcessRemoteRepoGclStderr = remoteProcessRemoteRepoGcl.communicate()
        if len(remoteProcessRemoteRepoGclStdout) > 0:
            logging.info(remoteProcessRemoteRepoGclStdout)
        if len(remoteProcessRemoteRepoGclStderr) > 0:
            logging.warning(remoteProcessRemoteRepoGclStderr)
            logging.info("You may be able to ignore the above warning.")
        remoteProcessRemoteRepoGbm = Popen(["git", "branch", "-m", "master", repo['primaryBranchName']], cwd=f"{localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}",
                                           stdout=PIPE, stderr=PIPE)
        logging.info(
            f"cwd={localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}: git branch -m master {repo['primaryBranchName']}")
        remoteProcessRemoteRepoGbmStdout, remoteProcessRemoteRepoGbmStderr = remoteProcessRemoteRepoGbm.communicate()
        if len(remoteProcessRemoteRepoGbmStdout) > 0:
            logging.info(remoteProcessRemoteRepoGbmStdout)
        if len(remoteProcessRemoteRepoGbmStderr) > 0:
            logging.warning(remoteProcessRemoteRepoGbmStderr)
            repo['error'] = True
            return
        remoteProcessRemoteRepoGpuo = Popen(["git", "push", "-u", "origin", repo['primaryBranchName']], cwd=f"{localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}",
                                            stdout=PIPE, stderr=PIPE)
        logging.info(
            f"cwd={localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}: git branch -u origin {repo['primaryBranchName']}")
        remoteProcessRemoteRepoGpuoStdout, remoteProcessRemoteRepoGpuoStderr = remoteProcessRemoteRepoGpuo.communicate()
        if len(remoteProcessRemoteRepoGpuoStdout) > 0:
            logging.info(remoteProcessRemoteRepoGpuoStdout)
        if len(remoteProcessRemoteRepoGpuoStderr) > 0:
            logging.warning(remoteProcessRemoteRepoGpuoStderr)
            logging.info("You may be able to ignore the above warning.")
        url = constructPatchDefaultUrl(repo)
        data = json.dumps({"default_branch": f"{repo['primaryBranchName']}"})
        headers = constructHeaders(token)
        patchDefaultResponse = requests.patch(url, data=data, headers=headers)
        if patchDefaultResponse.status_code >= 400:
            logging.warning(
                f"{repo['htmlUrl']} default branch change failed, response status: {patchDefaultResponse.status_code}")
            repo['error'] = True
            return
        else:
            logging.info(
                f"Default branch for {repo['htmlUrl']} updated to {repo['primaryBranchName']}.")
            remoteProcessGpdm = Popen(
                ["git", "push", "--delete", "origin", "master"], cwd=f"{localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}", stdout=PIPE, stderr=PIPE)
            logging.info(
                f"cwd={localDirectory}/master-blaster-{username}/{repo['owner-login']}/{repo['name']}: git push --delete origin master")
            remoteProcessGpdmStdout, remoteProcessGpdmStderr = remoteProcessGpdm.communicate()
            if len(remoteProcessGpdmStdout) > 0:
                logging.info(remoteProcessGpdmStdout)
            if len(remoteProcessGpdmStderr) > 0:
                logging.warning(remoteProcessGpdmStderr)
                logging.info("You may be able to ignore the above warning.")


if len(reposAlreadyBlasted) > 0:
    print("""
    The following repos have already been blasted:
    """)
    for repo in reposAlreadyBlasted:
        print(repo['htmlUrl'])
    print("\n")

if len(reposWithErrors) > 0:
    print("""
    The following repos had errors that prevented any process to run on them:
    """)
    for repo in reposWithErrors:
        print(f"{repo['htmlUrl']} {repo['status']}")
    print("\n")

if len(reposReadyForLocal) > 0:
    print("""
    The following repos are ready to update primary branch and origin locally:
    """)
    for repo in reposReadyForLocal:
        print(repo['htmlUrl'])
    localIsAGo = questionary.confirm("Continue?").ask()
    if not localIsAGo:
        print("""
    Okay! You can run the program again if you change your mind!
        """)
    print("\n")

if len(reposReadyForLocalMasterDelete) > 0:
    print("""
    The following repos could have their local branch 'master' deleted:
    """)
    for repo in reposReadyForLocalMasterDelete:
        print(repo['htmlUrl'])
    localMasterDeleteIsANoGo = questionary.confirm(
        "Delete? Defaults to no.").ask()
    if not localMasterDeleteIsANoGo:
        print("""
    Okay! Local 'master' branches will be deleted!
        """)
    else:
        print("""
    Okay! You can run the program again if you change your mind!
        """)
    print("\n")

if len(reposReadyForRemote) > 0:
    print("""
    The following repos are ready to update the primary branch:
    """)
    for repo in reposReadyForRemote:
        print(repo['htmlUrl'])
    remoteIsAGo = questionary.confirm("Continue?").ask()
    if not remoteIsAGo:
        print("""
    Okay! It's a no-go for remote repos!
        """)
    print("\n")

if localIsAGo:
    for repo in reposReadyForLocal:
        localProcess(repo)
        if repo.get('error'):
            print(f"Error with {repo['htmlUrl']}!")
        else:
            print(f"Local process completed for {repo['htmlUrl']}")

if not localMasterDeleteIsANoGo:
    for repo in reposReadyForLocalMasterDelete:
        localMasterDeleteProcess(repo)
        if repo.get('error'):
            print(f"Error with {repo['htmlUrl']}!")
        else:
            print(f"Local master branch deleted for {repo['htmlUrl']}")

if remoteIsAGo:
    for repo in reposReadyForRemote:
        remoteProcess(repo)
        if failedToMakeTempDir == True:
            break
        if repo.get('error'):
            print(f"Error with {repo['htmlUrl']}!")
        else:
            print(f"Remote process completed for {repo['htmlUrl']}")

if confirmRemoveLocalDirectoriesAfter:
    removeLocalDirectoriesProcess = Popen(
        ["rm", "-dfRv", f"./master-blaster-{username}"], cwd=localDirectory,  stdout=PIPE, stderr=PIPE)
    logging.info(f"cwd={localDirectory}: rm -dfRv ./master-blaster-{username}")
    removeLocalDirectoriesProcessStdout, removeLocalDirectoriesProcessStderr = removeLocalDirectoriesProcess.communicate()
    # if len(removeLocalDirectoriesProcessStdout) > 0:
    # logging.info(removeLocalDirectoriesProcessStdout)
    # Overflow error
    if len(removeLocalDirectoriesProcessStderr) > 0:
        logging.warning(removeLocalDirectoriesProcessStderr)
        print("Error: Failed to rm temp dir!")


# * ``` Reporting! ``` * #

if localIsAGo:
    errors = 0
    for repo in reposReadyForLocal:
        if repo.get('error'):
            errors = errors + 1
    if errors == len(reposReadyForLocal):
        print(f"""
    All repos ready for local process had errors!
        """)
    elif errors > 0:
        print(f"""
    {errors} errors with repos ready for the local process!
        """)
        print(f"""
    {len(reposReadyForLocal) - errors} repos completed the local process!
        """)
    else:
        print(f"""
    {len(reposReadyForLocal)} repos completed the local process!
        """)

if not localMasterDeleteIsANoGo:
    errors = 0
    for repo in reposReadyForLocalMasterDelete:
        if repo.get('error'):
            errors = errors + 1
    if errors == len(reposReadyForLocalMasterDelete):
        print(f"""
    All repos ready for local master branch removal had errors!
        """)
    elif errors > 0:
        print(f"""
    {errors} errors with repos ready for local master branch removal!
        """)
        print(f"""
    {len(reposReadyForLocalMasterDelete) - errors} repos completed local master branch removal!
        """)
    else:
        print(f"""
    {len(reposReadyForLocalMasterDelete)} repos completed local master branch removal!
        """)

if remoteIsAGo:
    errors = 0
    for repo in reposReadyForRemote:
        if repo.get('error'):
            errors = errors + 1
    if errors == len(reposReadyForRemote):
        print(f"""
    All repos ready for remote process had errors!
        """)
    elif errors > 0:
        print(f"""
    {errors} errors with repos ready for the remote process!
        """)
        print(f"""
    {len(reposReadyForRemote) - errors} repos completed the remote process!
        """)
    else:
        print(f"""
    {len(reposReadyForRemote)} repos completed the remote process!
        """)

# * Add the `git new` alias! * #


def runGitNew():
    gitNewGcg = Popen(["git", "config", "--global", "alias.new", "'!git", "init"],
                      stdout=PIPE, stderr=PIPE)
    logging.info(f"git config --global alias.new !git init")
    gitNewGcgStdout, gitNewGcgStderr = gitNewGcg.communicate()
    if len(gitNewGcgStdout) > 0:
        logging.info(gitNewGcgStdout)
    if len(gitNewGcgStderr) > 0:
        logging.warning(gitNewGcgStderr)
        print(f"Error creating git ! {gitNewGcgStderr}")
        return
    gitNewGsh = Popen(["git", "symbolic-ref", "HEAD", f"refs/heads/{name}"],
                      stdout=PIPE, stderr=PIPE)
    logging.info(f"git symbolic-ref HEAD refs/heads/{name}")
    gitNewGshStdout, gitNewGshStderr = gitNewGsh.communicate()
    if len(gitNewGshStdout) > 0:
        logging.info(gitNewGshStdout)
    if len(gitNewGshStderr) > 0:
        logging.warning(gitNewGshStderr)
        print(f"Error creating git alias! {gitNewGshStderr}")
        return


if gitNew:
    runGitNew()

# * ``` Denoument! ``` * #

print("Check the log file at ./info.log for details!\n")
print("Thank you for using master-blaster!")

# // ! Testing! #
# if(len(currentBranch) > 0):
#     Popen(["git", "checkout", f"{currentBranch}"],
#           stdout=PIPE, stderr=PIPE)

sys.exit()
