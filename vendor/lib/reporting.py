import os
from pathlib import Path
import questionary
from vendor.lib.logging import logInfo
from vendor.lib.actions.shell import getLocalToken

# reporting #
# * Text! * #


def intro():
    """Print the license, intro blurb, and token blurb!"""
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

    introText = """
      Welcome to master-blaster! This program batch renames primary branches
      for GitHub users! We'll go through the options before making any changes!
  """
    print(introText)

    tokenExplanation = """
      Also, GitHub is deprecating password-based token generation! This is great for
      security, it just means you're going to have to go to GitHub.com and
      come back with an access token to run the program, and it's a couple of steps,
      still faster than doing each manually if you have a bunch of repos, though.
      Thank you!
  """
    print(tokenExplanation)


def getUsername(testing):
    """Get the GitHub username and return it."""
    # * ``` Placeholder variable for the username! ``` * #
    username = ""

    def usernameConfirmationPrompt(usernameInput):
        return f"Confirm username: {usernameInput}"

    # * ``` Ask for username! ``` * #
    usernamePrompt = """
      First, please enter your GitHub username!
  """

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
                if not testing:
                    logInfo(f"Username: {username}")
                    usernameConfirmed = True
                    continue

    if testing:
        username = "Twitchkidd"
        logInfo(f"Username: {username}")

    return username


def getToken(testing):
    """Get token from user, validate, return tuple of token and repos."""
    token = ""

    tokenPrompt = """
    -- Token-getting time! --

    For good security, password-based token generation is being
    deprecated, so these are the steps to get a personal access
    token with the correct scope:

    Browse to https://github.com, sign in, then go to 'Settings',
    then 'Developer Settings', then 'Personal access tokens',
    then 'Generate new token', confirm your password, select the
    'repo' scope, then 'Generate Token', then copy that to clipboard.

    To avoid repeat in case of network error, save it somewhere first,
    then paste it back here into the prompt and hit enter to continue:

    For thorough and visual instructions in the GitHub docs,
    see the personal access tokens part: https://bit.ly/2X0cr3j
    
    """

    tokenConfirmed = False
    while not tokenConfirmed:
        customTokenResponse = questionary.text(tokenPrompt).ask()
        if customTokenResponse == "":
            print("Please enter the token!")
            continue
        else:
            token = customTokenResponse
            tokenConfirmed = True
            continue

    if testing:
        token = getLocalToken()

    return token


def repoTypesBlurb():
    """Explain all repos, owner, public/private."""
    print(
        "Currently the only supported set of repos is all repos user is owner of, public and private."
    )


def getNamingMode(main, custom, perRepo):
    return questionary.select(
        "What would you like to name your primary branches? (Default 'main'.)",
        choices=[main, custom, perRepo],
    ).ask()


def getCustomName():
    """For when the user wants to set all repos primary branches to a custom name."""
    name = "main"
    customNamePrompt = """
      What name are you choosing for primary branches?
  """
    confirmResetToMainPrompt = """
      Default: use 'main' for all primary branches?
  """

    def customNameConfirmPrompt(inputName):
        return f"""{inputName} for all primary branches?"""

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
        else:
            confirmCustomNameResponse = questionary.confirm(
                customNameConfirmPrompt(customNameResponse)
            ).ask()
            if confirmCustomNameResponse:
                name = customNameResponse
                nameConfirmed = True
    logInfo(f"Name for primary branches: {name}")
    return name


def getCustomNames(repos):
    """For when the user wants to set a custom name for each repo primary branch."""
    print(
        """
        Interactive naming mode!
    """
    )
    name = "main"
    for repo in repos:
        targetNameConfirmed = False
        while not targetNameConfirmed:
            repoNameResponse = questionary.text(
                f"Primary branch name for {repo['htmlUrl']}?"
            ).ask()
            if repoNameResponse == "":
                defaultNameResponse = questionary.confirm(
                    f"Default primary branch name {name} for {repo['htmlUrl']}?"
                )
                if defaultNameResponse:
                    repo["targetName"] = name
                    logInfo(f"Primary branch name for {repo['htmlUrl']}: {name}")
                    targetNameConfirmed = True
            else:
                customRepoNameConfirmed = questionary.confirm(
                    f"{repoNameResponse} for {repo['htmlUrl']}?"
                )
                if customRepoNameConfirmed:
                    repo["targetName"] = repoNameResponse
                    logInfo(
                        f"Primary branch name for {repo['htmlUrl']}: {repoNameResponse}"
                    )
                    targetNameConfirmed = True
    return repos


def getLocalDirectory(testing):
    """Local directories prompt. If yes, which local directory or default? Test that local directory is real."""
    localDirectory = ""
    localDirectoriesPrompt = """
        Repositories not present locally will be cloned to a temporary folder,
        updated, the update pushed, (the default branch on GitHub.com updated,) and
        then deleted locally depending on your choice in just a moment.
        
        To potentially decrease use of bandwidth and reduce conflicts, master-blaster
        can scan for repositories present locally, starting from the home folder or a
        specified code directory. Yes, or everything from the cloud?
    """
    localDirectories = questionary.confirm(localDirectoriesPrompt).ask()
    if not localDirectories:
        return None
    localDirectoryPrompt = """
        Do you keep all of your coding projects in a certain directory? Type that in
        here to limit and speed up search. Default is home, ~/, hit enter for default.
        Example: /Users/gareth/Code
    """
    confirmResetToHomePrompt = """
        Default: use '~/' for local directory search?
    """

    def customLocalDirectoryConfirmPrompt(inputDir):
        return f"""Use '{inputDir}' for local directory search?"""

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
        else:
            if os.path.isdir(customLocalDirectoryResponse):
                confirmCustomLocalDirectoryResponse = questionary.confirm(
                    customLocalDirectoryConfirmPrompt(customLocalDirectoryResponse)
                ).ask()
                if confirmCustomLocalDirectoryResponse:
                    localDirectory = customLocalDirectoryResponse
                    localDirectoryConfirmed = True
            else:
                print(
                    f"Error! Directory not showing as valid: {customLocalDirectoryResponse}"
                )
    if testing:
        localDirectory = f"{Path.home()}/Code"
    logInfo(f"Local directory to search: {localDirectory}")
    return localDirectory


def getRemoveClones(testing):
    confirmRemoveClonesPrompt = """
        Remove newly cloned repositories after process complete? Defaults to yes.
    """
    confirmRemoveClones = questionary.confirm(confirmRemoveClonesPrompt).ask()
    if testing:
        confirmRemoveClones = True
    logInfo(f"Confirm remove clones after: {confirmRemoveClones}")
    return confirmRemoveClones


def getGitNew(namingMode, perRepo, name, testing):
    if namingMode == perRepo:
        return False
    gitNew = True
    gitNewPrompt = f"""
        Add a git alias 'git new' that initializes
        new git repos with commit as {name}? Defaults to yes.
    """
    gitNew = questionary.confirm(gitNewPrompt)
    if testing:
        gitNew = True
    if gitNew:
        logInfo(f"Add git alias `git new`: {name}")
    return gitNew


def checkNames(repos):
    """This tests repos against various states and prompts for any actions that
    can be caught by looking at any naming errors."""

    # Repo object [ones in brackets are only conditionally present]:
    #   default
    #   htmlUrl
    #   name
    #   owner-login
    #   targetName
    #   [status] # local folder with name, can't read .git/config
    #   [configUrl]
    #   [localPath]
    #   [currentBranch]
    #   hasMaster
    #   hasTarget
    #   [localHasMaster]
    #   [localHasTarget]
    #   [[localHasThird]]

    #   These matter:
    #   [status] # local folder with name, can't read .git/config
    #   default
    #   hasMaster
    #   hasTarget
    #   [localHasMaster]
    #   [localHasTarget]
    #   [[localHasThird]]

    # Clear states:
    #   "remote process" "local repo"
    #       localHasMaster
    #       not localHasTarget
    #       hasMaster
    #       not hasTarget
    #       default is master
    #   "remote process" "clone repo"
    #       no localPath
    #       hasMaster
    #       not hasTarget
    #       default is master
    #   "local process"
    #       localHasMaster
    #       not localHasTarget
    #       hasTarget
    #       not hasMaster
    #       default is target
    #   "delete master" "local repo"
    #       localHasMaster
    #       localHasTarget
    #       hasTarget
    #       not hasMaster
    #       default is target
    #   "delete master" "remote repo"
    #       [localHasTarget
    #       not localHasMaster]
    #       hasTarget
    #       hasMaster
    #       default is target

    # States:
    #   [status] present: local folder with name can't read .git/config
    #     "local repo but not git folder"
    #
    #   both hasMaster and hasTarget, default is target: delete master?
    #   both 1) Delete local and remote?
    #       hasMaster
    #       hasTarget
    #       defaultTarget
    #       localHasMaster
    #       localHasTarget
    #   both 2) Delete remote?
    #       hasMaster
    #       hasTarget
    #       defaultTarget
    #       not localHasMaster
    #       localHasTarget
    #   both 3) Path unclear.
    #       hasMaster
    #       hasTarget
    #       defaultTarget
    #       localHasMaster
    #       not localHasTarget
    #   both 4) Could offer to delete remote, possibly do nothing though because that's weird about local.
    #       hasMaster
    #       hasTarget
    #       defaultTarget
    #       not localHasMaster
    #       not localHasTarget
    #   both 5) Delete remote?
    #       hasMaster
    #       hasTarget
    #       defaultTarget
    #       not localPath
    #
    #   both hasMaster and hasTarget, default is master
    #       make target default and delete master?
    #       NO, the path for merging isn't clear in any case.
    #
    #   both and default third
    #       no clear path.
    #       basically if third is default, except in the clear cases of neither 3), 7), and 9), no clear path.
    #
    #   Neither has master nor target, default is third
    #   neither 1) Status: local has all three, figure this one out yourself, user.
    #       not hasMaster
    #       not hasTarget
    #       default is third
    #       localHasMaster
    #       localHasTarget
    #       localHasThird
    #   neither 2) Status: do you want to mv target to third? Unclear path.
    #       not hasMaster
    #       not hasTarget
    #       default is third
    #       not localHasMaster
    #       localHasTarget
    #       localHasThird
    #   neither 3) Status: do you want to mv third to target and blast all the masters? Local repo
    #       not hasMaster
    #       not hasTarget
    #       default is third
    #       localHasMaster
    #       not localHasTarget
    #       localHasThird
    #   neither 4) Status: unclear path.
    #       not hasMaster
    #       not hasTarget
    #       default is third
    #       localHasMaster
    #       localHasTarget
    #       not localHasThird
    #   neither 5) Status: unclear path.
    #       not hasMaster
    #       not hasTarget
    #       default is third
    #       not localHasMaster
    #       localHasTarget
    #       not localHasThird
    #   neither 6) Status: unclear path.
    #       not hasMaster
    #       not hasTarget
    #       default is third
    #       localHasMaster
    #       not localHasTarget
    #       not localHasThird
    #   neither 7) Status: do you want to mv third to target? Local repo
    #       not hasMaster
    #       not hasTarget
    #       default is third
    #       not localHasMaster
    #       not localHasTarget
    #       localHasThird
    #   neither 8) Status: unclear path.
    #       not hasMaster
    #       not hasTarget
    #       default is third
    #       not localHasMaster
    #       not localHasTarget
    #       not localHasThird
    #   neither 9) Status: do you want to mv third to target? Clone repo
    #       not hasMaster
    #       not hasTarget
    #       default is third
    #       no localPath
    #
    #   Has master, no target, master is default
    #   master and default 1) Path unclear.
    #       hasMaster
    #       not hasTarget
    #       default is master
    #       localHasMaster
    #       localHasTarget
    #   master and default 2) Path unclear.
    #       hasMaster
    #       not hasTarget
    #       default is master
    #       not localHasMaster
    #       localHasTarget
    #   master and default 3) Perfect remote process local repo.
    #       hasMaster
    #       not hasTarget
    #       default is master
    #       localHasMaster
    #       not localHasTarget
    #   master and default 4) Path unclear.
    #       hasMaster
    #       not hasTarget
    #       default is master
    #       not localHasMaster
    #       not localHasTarget
    #   master and default 5) Perfect remote process clone repo.
    #       hasMaster
    #       not hasTarget
    #       default is master
    #       no localPath
    #
    #   Has target, no master, target is default
    #   target and default 1) Delete local master?
    #       not hasMaster
    #       hasTarget
    #       default is target
    #       localHasMaster
    #       localHasTarget
    #   target and default 2) Already blasted.
    #       not hasMaster
    #       hasTarget
    #       default is target
    #       not localHasMaster
    #       localHasTarget
    #   target and default 3) Perfect case local process.
    #       not hasMaster
    #       hasTarget
    #       default is target
    #       localHasMaster
    #       not localHasTarget
    #   target and default 4) Path unclear.
    #       not hasMaster
    #       hasTarget
    #       default is target
    #       not localHasMaster
    #       not localHasTarget
    #   target and default 5) Already blasted.
    #       not hasMaster
    #       hasTarget
    #       default is target
    #       no localPath
    #
    #   Everything else should error out, neither hasTarget and not hasMaster and default is master
    #       nor hasMaster and not hasTarget and default is target make sense, and there's no clear path
    #       for any third default that's not caught above.
    #

    states = {
        "pendingMvThirdToTargetLocal": "Do you want to mv third to target? Local repo",
        "mvThirdToTargetLocal": "Move third to target, local repo.",
        "pendingMvThirdToTargetClone": "Do you want to mv third to target? Clone repo",
        "mvThirdToTargetClone": "Move third to target, clone repo.",
        "pendingMvThirdToTargetAndBlastLocalMaster": "Do you want to mv third to target and blast the local master? Local repo.",
        "mvThirdToTargetAndBlastLocalMaster": "Move third to target and blast the local master, local repo.",
        "pendingDeleteRemote": "Delete remote?",
        "deleteRemote": "Delete remote.",
        "pendingDeleteLocal": "Delete local?",
        "deleteLocal": "Delete local.",
        "pendingDeleteLocalAndRemote": "Delete local and remote?",
        "deleteLocalAndRemote": "Delete local and remote.",
        "remoteProcessLocal": "Perfect remote process local repo.",
        "remoteProcessClone": "Perfect remote process clone repo.",
        "pendingLocalProcess": "Perfect case local process.",
        "localProcess": "Local process is a go.",
        "alreadyBlasted": "Already blasted.",
        "pathUnclear": "Path unclear.",
    }

    reposMvThirdToTargetLocal = {"pending": True, "repos": [], "errors": []}
    reposMvThirdToTargetClone = {"pending": True, "repos": [], "errors": []}
    reposMvThirdToTargetAndBlastLocalMaster = {
        "pending": True,
        "repos": [],
        "errors": [],
    }
    reposDeleteRemote = {"pending": True, "repos": [], "errors": []}
    reposDeleteLocal = {"pending": True, "repos": [], "errors": []}
    reposDeleteLocalAndRemote = {"pending": True, "repos": [], "errors": []}
    reposLocalProcess = {"pending": True, "repos": [], "errors": []}

    for repo in repos:
        if repo["status"]:
            continue
        if not repo["hasTarget"] and not repo["hasMaster"]:
            if repo["localPath"]:
                if (
                    repo["localHasMaster"]
                    and not repo["localHasTarget"]
                    and repo["localHasThird"]
                ):
                    repo["status"] = states.pendingMvThirdToTargetAndBlastLocalMaster
                    reposMvThirdToTargetAndBlastLocalMaster.repos.append(repo)
                    continue
                if (
                    not repo["localHasMaster"]
                    and not repo["localHasTarget"]
                    and repo["localHasThird"]
                ):
                    repo["status"] = states.pendingMvThirdToTargetLocal
                    reposMvThirdToTargetLocal.repos.append(repo)
                    continue
            else:
                repo["status"] = states.pendingMvThirdToTargetClone
                reposMvThirdToTargetClone.repos.append(repo)
                continue
        if repo["default"] != repo["targetName"] and repo["default"] != "master":
            repo["status"] = states.pathUnclear
        if (
            repo["hasTarget"]
            and repo["hasMaster"]
            and repo["default"] == repo["targetName"]
        ):
            if repo["localPath"]:
                if repo["localHasTarget"] and repo["localHasMaster"]:
                    repo["status"] = states.pendingDeleteLocalAndRemote
                    reposDeleteLocalAndRemote.repos.append(repo)
                    continue
                if not repo["localHasTarget"] and repo["localHasMaster"]:
                    repo["status"] = states.pendingDeleteRemote
                    reposDeleteRemote.repos.append(repo)
                    continue
                repo["status"] = states.pathUnclear
                continue
            repo["status"] = states.pendingDeleteRemote
            reposDeleteRemote.repos.append(repo)
            continue
        if repo["hasMaster"] and not repo["hasTarget"] and repo["default"] == "master":
            if repo["localPath"]:
                if repo["localHasMaster"] and not repo["localHasTarget"]:
                    repo["status"] = states.remoteProcessLocal
                    continue
                repo["status"] = states.pathUnclear
                continue
            repo["status"] = states.remoteProcessClone
            continue
        if (
            repo["hasTarget"]
            and not repo["hasMaster"]
            and repo["default"] == repo["targetName"]
        ):
            if repo["localPath"]:
                if repo["localHasMaster"] and repo["localHasTarget"]:
                    repo["status"] = states.pendingDeleteLocal
                    reposDeleteLocal.repos.append(repo)
                    continue
                if repo["localHasTarget"] and not repo["localHasMaster"]:
                    repo["status"] = states.alreadyBlasted
                    continue
                if not repo["localHasTarget"] and repo["localHasMaster"]:
                    repo["status"] = states.pendingLocalProcess
                    reposLocalProcess.repos.append(repo)
                repo["status"] = states.pathUnclear
                continue
            repo["status"] = states.alreadyBlasted
            continue
        repo["status"] = states.pathUnclear

    for repo in repos:
        logInfo(f"{repo['name']} initial status determined: {repo['status']}")

    if len(reposMvThirdToTargetLocal.repos) > 0:
        if len(reposMvThirdToTargetLocal.repos) > 1:
            print(
                "The following repos have a third name for their primary branch, which is present locally."
            )
        else:
            print(
                "The following repo has a third name for its primary branch, which is present locally."
            )
        for repo in reposMvThirdToTargetLocal.repos:
            print(repo["name"])
        decision = False
        if len(reposMvThirdToTargetLocal.repos) > 1:
            decision = questionary.confirm("Do you want to rename these branches?")
        else:
            decision = questionary.confirm("Do you want to rename this branch?")
        if decision:
            reposMvThirdToTargetLocal.pending = False
            for pendingRepo in reposMvThirdToTargetLocal.repos:
                for repo in repos:
                    if pendingRepo["name"] == repo["name"]:
                        repo["status"] = states.mvThirdToTargetLocal
                        logInfo(
                            f"{repo['name']} added to repos with status: {states.mvThirdToTargetLocal}"
                        )

    if len(reposMvThirdToTargetClone.repos) > 0:
        if len(reposMvThirdToTargetClone.repos) > 1:
            print("The following repos have a third name for their primary branch.")
        else:
            print("The following repo has a third name for its primary branch.")
        for repo in reposMvThirdToTargetClone.repos:
            print(repo["name"])
        decision = False
        if len(reposMvThirdToTargetClone.repos) > 1:
            decision = questionary.confirm("Do you want to rename these branches?")
        else:
            decision = questionary.confirm("Do you want to rename this branch?")
        if decision:
            reposMvThirdToTargetClone.pending = False
            for pendingRepo in reposMvThirdToTargetClone.repos:
                for repo in repos:
                    if pendingRepo["name"] == repo["name"]:
                        repo["status"] = states.mvThirdToTargetClone
                        logInfo(
                            f"{repo['name']} added to repos with status: {states.mvThirdToTargetClone}"
                        )

    if len(reposMvThirdToTargetAndBlastLocalMaster.repos) > 0:
        if len(reposMvThirdToTargetAndBlastLocalMaster.repos) > 1:
            print(
                "The following repos have a third name for their primary branch, which is present locally, and a locally present master branch."
            )
        else:
            print(
                "The following repo has a third name for its primary branch, which is present locally, and a locally present master branch."
            )
        for repo in reposMvThirdToTargetAndBlastLocalMaster.repos:
            print(repo["name"])
        decision = False
        if len(reposMvThirdToTargetAndBlastLocalMaster.repos) > 1:
            decision = questionary.confirm("Do you want to rename these branches?")
        else:
            decision = questionary.confirm("Do you want to rename this branch?")
        if decision:
            reposMvThirdToTargetAndBlastLocalMaster.pending = False
            for pendingRepo in reposMvThirdToTargetAndBlastLocalMaster.repos:
                for repo in repos:
                    if pendingRepo["name"] == repo["name"]:
                        repo["status"] = states.mvThirdToTargetAndBlastLocalMaster
                        logInfo(
                            f"{repo['name']} added to repos with status: {states.mvThirdToTargetAndBlastLocalMaster}"
                        )

    if len(reposDeleteRemote.repos) > 0:
        if len(reposDeleteRemote.repos) > 1:
            print("The following repos have a remote master branch.")
        else:
            print("The following repo has a remote master branch.")
        for repo in reposDeleteRemote.repos:
            print(repo["name"])
        decision = False
        if len(reposDeleteRemote.repos) > 1:
            decision = questionary.confirm("Do you want to delete these branches?")
        else:
            decision = questionary.confirm("Do you want to delete this branch?")
        if decision:
            reposDeleteRemote.pending = False
            for pendingRepo in reposDeleteRemote.repos:
                for repo in repos:
                    if pendingRepo["name"] == repo["name"]:
                        repo["status"] = states.deleteRemote
                        logInfo(
                            f"{repo['name']} added to repos with status: {states.deleteRemote}"
                        )

    if len(reposDeleteLocal.repos) > 0:
        if len(reposDeleteLocal.repos) > 1:
            print("The following repos have a local master branch.")
        else:
            print("The following repo has a local master branch.")
        for repo in reposDeleteLocal.repos:
            print(repo["name"])
        decision = False
        if len(reposDeleteLocal.repos) > 1:
            decision = questionary.confirm("Do you want to delete these branches?")
        else:
            decision = questionary.confirm("Do you want to delete this branch?")
        if decision:
            reposDeleteLocal.pending = False
            for pendingRepo in reposDeleteLocal.repos:
                for repo in repos:
                    if pendingRepo["name"] == repo["name"]:
                        repo["status"] = states.deleteLocal
                        logInfo(
                            f"{repo['name']} added to repos with status: {states.deleteLocal}"
                        )

    if len(reposDeleteLocalAndRemote.repos) > 0:
        if len(reposDeleteLocalAndRemote.repos) > 1:
            print("The following repos have a local and remote master branches.")
        else:
            print("The following repo has a local and remote master branch.")
        for repo in reposDeleteLocalAndRemote.repos:
            print(repo["name"])
        if questionary.confirm("Do you want to delete these branches?"):
            reposDeleteLocalAndRemote.pending = False
            for pendingRepo in reposDeleteLocalAndRemote.repos:
                for repo in repos:
                    if pendingRepo["name"] == repo["name"]:
                        repo["status"] = states.deleteLocalAndRemote
                        logInfo(
                            f"{repo['name']} added to repos with status: {states.deleteLocalAndRemote}"
                        )

    if len(reposLocalProcess.repos) > 0:
        if len(reposLocalProcess.repos) > 1:
            print("The following repos have local repos that can be updated.")
        else:
            print("The following repo has a local repo that can be updated.")
        for repo in reposLocalProcess.repos:
            print(repo["name"])
        decision = False
        if len(reposLocalProcess.repos) > 1:
            decision = questionary.confirm("Do you want to update these repos?")
        else:
            decision = questionary.confirm("Do you want to update this repo?")
        if decision:
            reposLocalProcess.pending = False
            for pendingRepo in reposLocalProcess.repos:
                for repo in repos:
                    if pendingRepo["name"] == repo["name"]:
                        repo["status"] = states.localProcess
                        logInfo(
                            f"{repo['name']} added to repos with status: {states.localProcess}"
                        )

    optionRepos = {
        "reposMvThirdToTargetLocal": reposMvThirdToTargetLocal,
        "reposMvThirdToTargetClone": reposMvThirdToTargetClone,
        "reposMvThirdToTargetAndBlastLocalMaster": reposMvThirdToTargetAndBlastLocalMaster,
        "reposDeleteRemote": reposDeleteRemote,
        "reposDeleteLocal": reposDeleteLocal,
        "reposDeleteLocalAndRemote": reposDeleteLocalAndRemote,
        "reposLocalProcess": reposLocalProcess,
    }
    return repos, optionRepos


def reportOn(finalRepos):
    """TODO"""


def denoument():
    print("Thank you for using master-blaster!\n")
    print("Check the log file at ./info.log for details!")
