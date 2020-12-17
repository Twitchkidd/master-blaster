import logging
import os
from pathlib import Path
import questionary
from vendor.lib.actions.shell import get_local_token


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


def get_username(testing):
    """Get the GitHub username and return it."""
    usernamePrompt = """
      First, please enter your GitHub username!
  """

    username = ""
    while True:
        username = questionary.text(usernamePrompt).ask()
        if username == "":
            print("GitHub username blank: Please try again!")
            continue
        if len(username) >= 40:
            print("GitHub usernames are 39 chars or less: please try again!")
            continue
        usernameConfirmed = questionary.confirm(f"Confirm username: {username}").ask()
        if usernameConfirmed == False:
            print("Thank you for retrying!")
            continue
        if usernameConfirmed:
            if not testing:
                logging.info(f"Username: {username}")
                break
            if testing:
                break

    if testing:
        username = "Twitchkidd"
        logging.info(f"Username: {username}")

    return username


def get_token(testing):
    """Get token from user, validate, return tuple of token and repos."""

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

    token = ""
    while True:
        token = questionary.password(tokenPrompt).ask()
        if token == "":
            print("Please enter the token!")
            continue
        else:
            break

    if testing:
        localTokenAttempt = get_local_token()
        if localTokenAttempt != None:
            token = localTokenAttempt

    return token


def repo_types_blurb():
    """Explain all repos, owner, public/private."""
    print(
        "Currently the only supported set of repos is all repos user is owner of, public and private.\n"
    )


def get_naming_mode(main, custom, perRepo):
    return questionary.select(
        "What would you like to name your primary branches? (Default 'main'.)",
        choices=[main, custom, perRepo],
    ).ask()


def custom_name_confirm_prompt(inputName):
    return f"""{inputName} for all primary branches?"""


def get_custom_name():
    """For when the user wants to set all repos primary branches to a custom name."""

    customNamePrompt = """
      What name are you choosing for primary branches?
  """
    confirmResetToMainPrompt = """
      Default: use 'main' for all primary branches?
  """

    name = "main"
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
                custom_name_confirm_prompt(customNameResponse)
            ).ask()
            if confirmCustomNameResponse:
                name = customNameResponse
                nameConfirmed = True
    logging.info(f"Name for primary branches: {name}")
    return name


def get_custom_names(repos):
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
                    logging.info(f"Primary branch name for {repo['htmlUrl']}: {name}")
                    targetNameConfirmed = True
            else:
                customRepoNameConfirmed = questionary.confirm(
                    f"{repoNameResponse} for {repo['htmlUrl']}?"
                )
                if customRepoNameConfirmed:
                    repo["targetName"] = repoNameResponse
                    logging.info(
                        f"Primary branch name for {repo['htmlUrl']}: {repoNameResponse}"
                    )
                    targetNameConfirmed = True
    return repos


def get_local_directory(testing):
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

    def custom_local_directory_confirm_prompt(inputDir):
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
                    custom_local_directory_confirm_prompt(customLocalDirectoryResponse)
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
    logging.info(f"Local directory to search: {localDirectory}")
    return localDirectory


def get_remove_clones(testing):
    confirmRemoveClonesPrompt = """
        Remove newly cloned repositories after process complete? Defaults to yes.
    """
    confirmRemoveClones = questionary.confirm(confirmRemoveClonesPrompt).ask()
    if testing:
        confirmRemoveClones = True
    logging.info(f"Confirm remove clones after: {confirmRemoveClones}")
    return confirmRemoveClones


def get_git_new(namingMode, perRepo, name, testing):
    if namingMode == perRepo:
        return False
    gitNew = True
    gitNewPrompt = f"""
        Add a git alias 'git new' that initializes
        new git repos with HEAD as {name}? Defaults to yes.
    """
    gitNew = questionary.confirm(gitNewPrompt).ask()
    if testing:
        gitNew = True
    if gitNew:
        logging.info(f"Add git alias `git new`: {name}")
    return gitNew


def check_names(repos):
    """This tests repos against various states and prompts for any actions that
    can be caught by looking at any naming errors."""
    # >> Repo object [ones in brackets are only conditionally present]:
    #      default
    #      htmlUrl
    #      name
    #      owner-login
    #      targetName
    #      [status] # local folder with name, can't read .git/config
    #      [configUrl]
    #      [localPath]
    #      [currentBranch]
    #      hasMaster
    #      hasTarget
    #      [localHasMaster]
    #      [localHasTarget]
    #      [[localHasThird]]

    # >> These matter:
    #      [status] # local folder with name, can't read .git/config
    #      default
    #      hasMaster
    #      hasTarget
    #      [localHasMaster]
    #      [localHasTarget]
    #      [[localHasThird]]

    # * Clear states:
    # *   "remote process" "local repo"
    # *       localHasMaster
    # *       not localHasTarget
    # *       hasMaster
    # *       not hasTarget
    # *       default is master
    # *   "remote process" "clone repo"
    # *       no localPath
    # *       hasMaster
    # *       not hasTarget
    # *       default is master
    # *   "local process"
    # *       localHasMaster
    # *       not localHasTarget
    # *       hasTarget
    # *       not hasMaster
    # *       default is target
    # *   "delete master" "local repo"
    # *       localHasMaster
    # *       localHasTarget
    # *       hasTarget
    # *       not hasMaster
    # *       default is target
    # *   "delete master" "remote repo"
    # *       [localHasTarget
    # *       not localHasMaster]
    # *       hasTarget
    # *       hasMaster
    # *       default is target

    # * States:
    # *   [status] present: local folder with name can't read .git/config
    # *     "local repo but not git folder"
    # *
    # *   both hasMaster and hasTarget, default is target: delete master?
    # *   both 1) Delete local and remote?
    # *       hasMaster
    # *       hasTarget
    # *       defaultTarget
    # *       localHasMaster
    # *       localHasTarget
    # *   both 2) Delete remote?
    # *       hasMaster
    # *       hasTarget
    # *       defaultTarget
    # *       not localHasMaster
    # *       localHasTarget
    # *   both 3) Path unclear.
    # *       hasMaster
    # *       hasTarget
    # *       defaultTarget
    # *       localHasMaster
    # *       not localHasTarget
    # *   both 4) Could offer to delete remote, possibly do nothing though because that's weird about local.
    # *       hasMaster
    # *       hasTarget
    # *       defaultTarget
    # *       not localHasMaster
    # *       not localHasTarget
    # *   both 5) Delete remote?
    # *       hasMaster
    # *       hasTarget
    # *       defaultTarget
    # *       not localPath
    # *
    # *   both hasMaster and hasTarget, default is master
    # *       make target default and delete master?
    # *       NO, the path for merging isn't clear in any case.
    # *
    # *   both and default third
    # *       no clear path.
    # *       basically if third is default, except in the clear cases of neither 3), 7), and 9), no clear path.
    # *
    # *   Neither has master nor target, default is third
    # *   neither 1) Status: local has all three, figure this one out yourself, user.
    # *       not hasMaster
    # *       not hasTarget
    # *       default is third
    # *       localHasMaster
    # *       localHasTarget
    # *       localHasThird
    # *   neither 2) Status: do you want to mv target to third? Unclear path.
    # *       not hasMaster
    # *       not hasTarget
    # *       default is third
    # *       not localHasMaster
    # *       localHasTarget
    # *       localHasThird
    # *   neither 3) Status: do you want to mv third to target and blast all the masters? Local repo
    # *       not hasMaster
    # *       not hasTarget
    # *       default is third
    # *       localHasMaster
    # *       not localHasTarget
    # *       localHasThird
    # *   neither 4) Status: unclear path.
    # *       not hasMaster
    # *       not hasTarget
    # *       default is third
    # *       localHasMaster
    # *       localHasTarget
    # *       not localHasThird
    # *   neither 5) Status: unclear path.
    # *       not hasMaster
    # *       not hasTarget
    # *       default is third
    # *       not localHasMaster
    # *       localHasTarget
    # *       not localHasThird
    # *   neither 6) Status: unclear path.
    # *       not hasMaster
    # *       not hasTarget
    # *       default is third
    # *       localHasMaster
    # *       not localHasTarget
    # *       not localHasThird
    # *   neither 7) Status: do you want to mv third to target? Local repo
    # *       not hasMaster
    # *       not hasTarget
    # *       default is third
    # *       not localHasMaster
    # *       not localHasTarget
    # *       localHasThird
    # *   neither 8) Status: unclear path.
    # *       not hasMaster
    # *       not hasTarget
    # *       default is third
    # *       not localHasMaster
    # *       not localHasTarget
    # *       not localHasThird
    # *   neither 9) Status: do you want to mv third to target? Clone repo
    # *       not hasMaster
    # *       not hasTarget
    # *       default is third
    # *       no localPath
    # *
    # *   Has master, no target, master is default
    # *   master and default 1) Path unclear.
    # *       hasMaster
    # *       not hasTarget
    # *       default is master
    # *       localHasMaster
    # *       localHasTarget
    # *   master and default 2) Path unclear.
    # *       hasMaster
    # *       not hasTarget
    # *       default is master
    # *       not localHasMaster
    # *       localHasTarget
    # *   master and default 3) Perfect remote process local repo.
    # *       hasMaster
    # *       not hasTarget
    # *       default is master
    # *       localHasMaster
    # *       not localHasTarget
    # *   master and default 4) Path unclear.
    # *       hasMaster
    # *       not hasTarget
    # *       default is master
    # *       not localHasMaster
    # *       not localHasTarget
    # *   master and default 5) Perfect remote process clone repo.
    # *       hasMaster
    # *       not hasTarget
    # *       default is master
    # *       no localPath
    # *
    # *   Has target, no master, target is default
    # *   target and default 1) Delete local master?
    # *       not hasMaster
    # *       hasTarget
    # *       default is target
    # *       localHasMaster
    # *       localHasTarget
    # *   target and default 2) Already blasted.
    # *       not hasMaster
    # *       hasTarget
    # *       default is target
    # *       not localHasMaster
    # *       localHasTarget
    # *   target and default 3) Perfect case local process.
    # *       not hasMaster
    # *       hasTarget
    # *       default is target
    # *       localHasMaster
    # *       not localHasTarget
    # *   target and default 4) Path unclear.
    # *       not hasMaster
    # *       hasTarget
    # *       default is target
    # *       not localHasMaster
    # *       not localHasTarget
    # *   target and default 5) Already blasted.
    # *       not hasMaster
    # *       hasTarget
    # *       default is target
    # *       no localPath
    # *
    # *   Everything else should error out, neither hasTarget and not hasMaster and default is master
    # *       nor hasMaster and not hasTarget and default is target make sense, and there's no clear path
    # *       for any third default that's not caught above.
    # *

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

    reposMvThirdToTargetLocal = {"pending": True, "repos": []}
    reposMvThirdToTargetClone = {"pending": True, "repos": []}
    reposMvThirdToTargetAndBlastLocalMaster = {"pending": True, "repos": []}
    reposDeleteRemote = {"pending": True, "repos": []}
    reposDeleteLocal = {"pending": True, "repos": []}
    reposDeleteLocalAndRemote = {"pending": True, "repos": []}
    reposLocalProcess = {"pending": True, "repos": []}

    for repo in repos:
        if repo.get("status"):
            if (
                repo["status"]
                == "Local folder that possibly isn't git repo, error opening .git/config"
            ):
                continue
        if not repo["hasTarget"] and not repo["hasMaster"]:
            if repo.get("localPath"):
                if (
                    repo["localHasMaster"]
                    and not repo["localHasTarget"]
                    and repo["localHasThird"]
                ):
                    repo["status"] = states["pendingMvThirdToTargetAndBlastLocalMaster"]
                    reposMvThirdToTargetAndBlastLocalMaster["repos"].append(repo)
                    continue
                if (
                    not repo["localHasMaster"]
                    and not repo["localHasTarget"]
                    and repo["localHasThird"]
                ):
                    repo["status"] = states["pendingMvThirdToTargetLocal"]
                    reposMvThirdToTargetLocal["repos"].append(repo)
                    continue
            else:
                repo["status"] = states["pendingMvThirdToTargetClone"]
                reposMvThirdToTargetClone["repos"].append(repo)
                continue
        if repo["default"] != repo["targetName"] and repo["default"] != "master":
            repo["status"] = states["pathUnclear"]
        if (
            repo["hasTarget"]
            and repo["hasMaster"]
            and repo["default"] == repo["targetName"]
        ):
            if repo.get("localPath"):
                if repo["localHasTarget"] and repo["localHasMaster"]:
                    repo["status"] = states["pendingDeleteLocalAndRemote"]
                    reposDeleteLocalAndRemote["repos"].append(repo)
                    continue
                if not repo["localHasTarget"] and repo["localHasMaster"]:
                    repo["status"] = states["pendingDeleteRemote"]
                    reposDeleteRemote["repos"].append(repo)
                    continue
                repo["status"] = states["pathUnclear"]
                continue
            repo["status"] = states["pendingDeleteRemote"]
            reposDeleteRemote["repos"].append(repo)
            continue
        if repo["hasMaster"] and not repo["hasTarget"] and repo["default"] == "master":
            if repo.get("localPath"):
                if repo["localHasMaster"] and not repo["localHasTarget"]:
                    repo["status"] = states["remoteProcessLocal"]
                    continue
                repo["status"] = states["pathUnclear"]
                continue
            repo["status"] = states["remoteProcessClone"]
            continue
        if (
            repo["hasTarget"]
            and not repo["hasMaster"]
            and repo["default"] == repo["targetName"]
        ):
            if repo.get("localPath"):
                if repo["localHasMaster"] and repo["localHasTarget"]:
                    repo["status"] = states["pendingDeleteLocal"]
                    reposDeleteLocal["repos"].append(repo)
                    continue
                if repo["localHasTarget"] and not repo["localHasMaster"]:
                    repo["status"] = states["alreadyBlasted"]
                    continue
                if not repo["localHasTarget"] and repo["localHasMaster"]:
                    repo["status"] = states["pendingLocalProcess"]
                    reposLocalProcess["repos"].append(repo)
                repo["status"] = states["pathUnclear"]
                continue
            repo["status"] = states["alreadyBlasted"]
            continue
        repo["status"] = states["pathUnclear"]

    for repo in repos:
        logging.info(f"{repo['name']} initial status determined: {repo['status']}")

    if reposMvThirdToTargetLocal.get("repos"):
        if len(reposMvThirdToTargetLocal["repos"]) > 0:
            if len(reposMvThirdToTargetLocal["repos"]) > 1:
                print(
                    "The following repos have a third name for their primary branch, which is present locally."
                )
            else:
                print(
                    "The following repo has a third name for its primary branch, which is present locally."
                )
            for repo in reposMvThirdToTargetLocal["repos"]:
                print(repo["name"])
            decision = False
            if len(reposMvThirdToTargetLocal["repos"]) > 1:
                decision = questionary.confirm("Do you want to rename these branches?")
            else:
                decision = questionary.confirm("Do you want to rename this branch?")
            if decision:
                reposMvThirdToTargetLocal["pending"] = False
                for pendingRepo in reposMvThirdToTargetLocal["repos"]:
                    for repo in repos:
                        if pendingRepo["name"] == repo["name"]:
                            repo["status"] = states["mvThirdToTargetLocal"]
                            logging.info(
                                f"{repo['name']} added to repos with status: {states['mvThirdToTargetLocal']}"
                            )

    if reposMvThirdToTargetClone.get("repos"):
        if len(reposMvThirdToTargetClone["repos"]) > 0:
            if len(reposMvThirdToTargetClone["repos"]) > 1:
                print("The following repos have a third name for their primary branch.")
            else:
                print("The following repo has a third name for its primary branch.")
            for repo in reposMvThirdToTargetClone["repos"]:
                print(repo["name"])
            decision = False
            if len(reposMvThirdToTargetClone["repos"]) > 1:
                decision = questionary.confirm("Do you want to rename these branches?")
            else:
                decision = questionary.confirm("Do you want to rename this branch?")
            if decision:
                reposMvThirdToTargetClone["pending"] = False
                for pendingRepo in reposMvThirdToTargetClone["repos"]:
                    for repo in repos:
                        if pendingRepo["name"] == repo["name"]:
                            repo["status"] = states["mvThirdToTargetClone"]
                            logging.info(
                                f"{repo['name']} added to repos with status: {states['mvThirdToTargetClone']}"
                            )

    if reposMvThirdToTargetAndBlastLocalMaster.get("repos"):
        if len(reposMvThirdToTargetAndBlastLocalMaster["repos"]) > 0:
            if len(reposMvThirdToTargetAndBlastLocalMaster["repos"]) > 1:
                print(
                    "The following repos have a third name for their primary branch, which is present locally, and a locally present master branch."
                )
            else:
                print(
                    "The following repo has a third name for its primary branch, which is present locally, and a locally present master branch."
                )
            for repo in reposMvThirdToTargetAndBlastLocalMaster["repos"]:
                print(repo["name"])
            decision = False
            if len(reposMvThirdToTargetAndBlastLocalMaster["repos"]) > 1:
                decision = questionary.confirm("Do you want to rename these branches?")
            else:
                decision = questionary.confirm("Do you want to rename this branch?")
            if decision:
                reposMvThirdToTargetAndBlastLocalMaster["pending"] = False
                for pendingRepo in reposMvThirdToTargetAndBlastLocalMaster["repos"]:
                    for repo in repos:
                        if pendingRepo["name"] == repo["name"]:
                            repo["status"] = states[
                                "mvThirdToTargetAndBlastLocalMaster"
                            ]
                            logging.info(
                                f"{repo['name']} added to repos with status: {states['mvThirdToTargetAndBlastLocalMaster']}"
                            )

    if reposDeleteRemote.get("repos"):
        if len(reposDeleteRemote["repos"]) > 0:
            if len(reposDeleteRemote["repos"]) > 1:
                print("The following repos have a remote master branch.")
            else:
                print("The following repo has a remote master branch.")
            for repo in reposDeleteRemote["repos"]:
                print(repo["name"])
            decision = False
            if len(reposDeleteRemote["repos"]) > 1:
                decision = questionary.confirm("Do you want to delete these branches?")
            else:
                decision = questionary.confirm("Do you want to delete this branch?")
            if decision:
                reposDeleteRemote["pending"] = False
                for pendingRepo in reposDeleteRemote["repos"]:
                    for repo in repos:
                        if pendingRepo["name"] == repo["name"]:
                            repo["status"] = states["deleteRemote"]
                            logging.info(
                                f"{repo['name']} added to repos with status: {states['deleteRemote']}"
                            )

    if reposDeleteLocal.get("repos"):
        if len(reposDeleteLocal["repos"]) > 0:
            if len(reposDeleteLocal["repos"]) > 1:
                print("The following repos have a local master branch.")
            else:
                print("The following repo has a local master branch.")
            for repo in reposDeleteLocal["repos"]:
                print(repo["name"])
            decision = False
            if len(reposDeleteLocal["repos"]) > 1:
                decision = questionary.confirm("Do you want to delete these branches?")
            else:
                decision = questionary.confirm("Do you want to delete this branch?")
            if decision:
                reposDeleteLocal["pending"] = False
                for pendingRepo in reposDeleteLocal["repos"]:
                    for repo in repos:
                        if pendingRepo["name"] == repo["name"]:
                            repo["status"] = states["deleteLocal"]
                            logging.info(
                                f"{repo['name']} added to repos with status: {states['deleteLocal']}"
                            )

    if reposDeleteLocalAndRemote.get("repos"):
        if len(reposDeleteLocalAndRemote["repos"]) > 0:
            if len(reposDeleteLocalAndRemote["repos"]) > 1:
                print("The following repos have a local and remote master branches.")
            else:
                print("The following repo has a local and remote master branch.")
            for repo in reposDeleteLocalAndRemote["repos"]:
                print(repo["name"])
            if questionary.confirm("Do you want to delete these branches?"):
                reposDeleteLocalAndRemote.pending = False
                for pendingRepo in reposDeleteLocalAndRemote["repos"]:
                    for repo in repos:
                        if pendingRepo["name"] == repo["name"]:
                            repo["status"] = states["deleteLocalAndRemote"]
                            logging.info(
                                f"{repo['name']} added to repos with status: {states['deleteLocalAndRemote']}"
                            )

    if reposLocalProcess.get("repos"):
        if len(reposLocalProcess["repos"]) > 0:
            if len(reposLocalProcess["repos"]) > 1:
                print("The following repos have local repos that can be updated.")
            else:
                print("The following repo has a local repo that can be updated.")
            for repo in reposLocalProcess["repos"]:
                print(repo["name"])
            decision = False
            if len(reposLocalProcess["repos"]) > 1:
                decision = questionary.confirm("Do you want to update these repos?")
            else:
                decision = questionary.confirm("Do you want to update this repo?")
            if decision:
                reposLocalProcess.pending = False
                for pendingRepo in reposLocalProcess["repos"]:
                    for repo in repos:
                        if pendingRepo["name"] == repo["name"]:
                            repo["status"] = states["localProcess"]
                            logging.info(
                                f"{repo['name']} added to repos with status: {states['localProcess']}"
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


def print_names_and_errors(repos):
    """Print out the names of successes, if present, then errors, if present."""
    reposNumber = 0
    if repos.get("repos"):
        reposNumber = len(repos["repos"])
    else:
        reposNumber = len(repos)
    repoErrorsNumber = 0
    if repos.get("errors"):
        repoErrorsNumber = len(repos.errors)
    if reposNumber > repoErrorsNumber:
        print(f"Successes: {reposNumber - repoErrorsNumber}\n")
        if repoErrorsNumber > 0:
            for repo in repos["repos"]:
                error = False
                for errorRepo in repos["errors"]:
                    if repo["name"] == errorRepo["name"]:
                        error = True
                if not error:
                    print(f"{repo['name']}\n")
            print(f"Errors: {repoErrorsNumber}\n")
            for errorRepo in repos["errors"]:
                print(f"{errorRepo['name']}\n")
        else:
            for repo in repos["repos"]:
                print(f"{repo['name']}\n")
    else:
        print(f"Errors: {repoErrorsNumber}\n")
        for errorRepo in repos["errors"]:
            print(f"{errorRepo['name']}\n")


def report_on(
    finalRepos, clonesRmAttempted, reposCloneDeletionError, gitNew, gitNewError
):
    """What happened?"""
    # states = {
    #     "pendingMvThirdToTargetLocal": "Do you want to mv third to target? Local repo",
    #     "mvThirdToTargetLocal": "Move third to target, local repo.",
    #     "pendingMvThirdToTargetClone": "Do you want to mv third to target? Clone repo",
    #     "mvThirdToTargetClone": "Move third to target, clone repo.",
    #     "pendingMvThirdToTargetAndBlastLocalMaster": "Do you want to mv third to target and blast the local master? Local repo.",
    #     "mvThirdToTargetAndBlastLocalMaster": "Move third to target and blast the local master, local repo.",
    #     "pendingDeleteRemote": "Delete remote?",
    #     "deleteRemote": "Delete remote.",
    #     "pendingDeleteLocal": "Delete local?",
    #     "deleteLocal": "Delete local.",
    #     "pendingDeleteLocalAndRemote": "Delete local and remote?",
    #     "deleteLocalAndRemote": "Delete local and remote.",
    #     "remoteProcessLocal": "Perfect remote process local repo.",
    #     "remoteProcessClone": "Perfect remote process clone repo.",
    #     "pendingLocalProcess": "Perfect case local process.",
    #     "localProcess": "Local process is a go.",
    #     "alreadyBlasted": "Already blasted.",
    #     "pathUnclear": "Path unclear.",
    #     "folderError": "Local folder that possibly isn't git repo, error opening .git/config",
    # }
    # finalRepos = {
    #     "reposRemoteProcessLocal": reposRemoteProcessLocal,
    #     "reposRemoteProcessClone": reposRemoteProcessClone,
    #     "reposDeleteLocal": optionRepos.reposDeleteLocal,
    #     "reposDeleteRemote": optionRepos.reposDeleteRemote,
    #     "reposDeleteLocalAndRemote": optionRepos.reposDeleteLocalAndRemote,
    #     "reposLocalProcess": optionRepos.reposLocalProcess,
    #     "reposMvThirdToTargetLocal": optionRepos.reposMvThirdToTargetLocal,
    #     "reposMvThirdToTargetClone": optionRepos.reposMvThirdToTargetClone,
    #     "reposMvThirdToTargetAndBlastLocalMaster": optionRepos.reposMvThirdToTargetAndBlastLocalMaster,
    #     "reposPathUnclear": reposPathUnclear,
    #     "reposFolderError": reposFolderError,
    #     "reposAlreadyBlasted": reposAlreadyBlasted,
    # }
    print("Process complete!\n")

    reposNumber = len(finalRepos["reposRemoteProcessLocal"]["repos"])
    repoErrorsNumber = len(finalRepos["reposRemoteProcessLocal"]["errors"])
    if len(reposNumber) > 0:
        if not len(repoErrorsNumber) > 0:
            if len(reposNumber > 1):
                print(f"{len(reposNumber)} repos blasted from local repos!")
            else:
                print(f"{len(reposNumber)} repo blasted from the local repo!")
        elif len(reposNumber) > len(repoErrorsNumber):
            if len(repoErrorsNumber) > 1:
                print(
                    f"Attempted to blast {len(reposNumber)} repos from local repos, succeeded with {len(reposNumber) - len(repoErrorsNumber)} while {len(repoErrorsNumber)} had errors!"
                )
            else:
                print(
                    f"Attempted to blast {len(reposNumber)} repos from local repos, succeeded with {len(reposNumber) - len(repoErrorsNumber)} while {len(repoErrorsNumber)} had an error!"
                )
        else:
            if len(reposNumber) > 1:
                print(
                    f"Attempted to blast {len(reposNumber)} repos from local repos, all errored!"
                )
            else:
                print(
                    f"Attempted to blast {len(reposNumber)} repo from the local repo and it errored!"
                )
    print_names_and_errors(finalRepos["reposRemoteProcessLocal"])

    reposNumber = len(finalRepos["reposRemoteProcessClone"]["repos"])
    repoErrorsNumber = len(finalRepos["reposRemoteProcessClone"]["errors"])
    if len(reposNumber) > 0:
        if not len(repoErrorsNumber) > 0:
            if len(reposNumber > 1):
                print(f"{len(reposNumber)} repos blasted by cloning the repos!")
            else:
                print(f"{len(reposNumber)} repo blasted by cloning the repo!")
        elif len(reposNumber) > len(repoErrorsNumber):
            if len(repoErrorsNumber) > 1:
                print(
                    f"Attempted to blast {len(reposNumber)} repos by cloning the repos, succeeded with {len(reposNumber) - len(repoErrorsNumber)} while {len(repoErrorsNumber)} had errors!"
                )
            else:
                print(
                    f"Attempted to blast {len(reposNumber)} repos by cloning the repos, succeeded with {len(reposNumber) - len(repoErrorsNumber)} while {len(repoErrorsNumber)} had an error!"
                )
        else:
            if len(reposNumber) > 1:
                print(
                    f"Attempted to blast {len(reposNumber)} repos by cloning the repos, all errored!"
                )
            else:
                print(
                    f"Attempted to blast {len(reposNumber)} repo by cloning the repo and it errored!"
                )
    print_names_and_errors(finalRepos["reposRemoteProcessClone"])

    reposNumber = len(finalRepos["reposDeleteLocal"]["repos"])
    repoErrorsNumber = len(finalRepos["reposDeleteLocal"]["errors"])
    if len(reposNumber) > 0:
        if not len(repoErrorsNumber) > 0:
            if len(reposNumber > 1):
                print(f"{len(reposNumber)} local master branches blasted!")
            else:
                print(f"{len(reposNumber)} local master branch blasted!")
        elif len(reposNumber) > len(repoErrorsNumber):
            if len(repoErrorsNumber) > 1:
                print(
                    f"Attempted to blast {len(reposNumber)} local master branches, succeeded with {len(reposNumber) - len(repoErrorsNumber)} while {len(repoErrorsNumber)} had errors!"
                )
            else:
                print(
                    f"Attempted to blast {len(reposNumber)} local master branches, succeeded with {len(reposNumber) - len(repoErrorsNumber)} while {len(repoErrorsNumber)} had an error!"
                )
        else:
            if len(reposNumber) > 1:
                print(
                    f"Attempted to blast {len(reposNumber)} local master branches, all errored!"
                )
            else:
                print(
                    f"Attempted to blast {len(reposNumber)} local master branch and it errored!"
                )
    print_names_and_errors(finalRepos["reposDeleteLocal"])

    reposNumber = len(finalRepos["reposDeleteRemote"]["repos"])
    repoErrorsNumber = len(finalRepos["reposDeleteRemote"]["errors"])
    if len(reposNumber) > 0:
        if not len(repoErrorsNumber) > 0:
            if len(reposNumber > 1):
                print(
                    f"{len(reposNumber)} master branches blasted by cloning the repos!"
                )
            else:
                print(f"{len(reposNumber)} master branch blasted by cloning the repo!")
        elif len(reposNumber) > len(repoErrorsNumber):
            if len(repoErrorsNumber) > 1:
                print(
                    f"Attempted to blast {len(reposNumber)} master branches by cloning the repos, succeeded with {len(reposNumber) - len(repoErrorsNumber)} while {len(repoErrorsNumber)} had errors!"
                )
            else:
                print(
                    f"Attempted to blast {len(reposNumber)} master branches by cloning the repos, succeeded with {len(reposNumber) - len(repoErrorsNumber)} while {len(repoErrorsNumber)} had an error!"
                )
        else:
            if len(reposNumber) > 1:
                print(
                    f"Attempted to blast {len(reposNumber)} master branches by cloning the repos, all errored!"
                )
            else:
                print(
                    f"Attempted to blast {len(reposNumber)} master branch by cloning the repo and it errored!"
                )
    print_names_and_errors(finalRepos["reposDeleteRemote"])

    reposNumber = len(finalRepos["reposDeleteLocalAndRemote"]["repos"])
    repoErrorsNumber = len(finalRepos["reposDeleteLocalAndRemote"]["errors"])
    if len(reposNumber) > 0:
        if not len(repoErrorsNumber) > 0:
            if len(reposNumber > 1):
                print(
                    f"{len(reposNumber)} master branches blasted in local repos and remotely!"
                )
            else:
                print(
                    f"{len(reposNumber)} master branch blasted in the local repo and remotely!"
                )
        elif len(reposNumber) > len(repoErrorsNumber):
            if len(repoErrorsNumber) > 1:
                print(
                    f"Attempted to blast {len(reposNumber)} master branches in a local repo and remotely, succeeded with {len(reposNumber) - len(repoErrorsNumber)} while {len(repoErrorsNumber)} had errors!"
                )
            else:
                print(
                    f"Attempted to blast {len(reposNumber)} master branches in a local repo and remotely, succeeded with {len(reposNumber) - len(repoErrorsNumber)} while {len(repoErrorsNumber)} had an error!"
                )
        else:
            if len(reposNumber) > 1:
                print(
                    f"Attempted to blast {len(reposNumber)} master branches in local repos and remotely, all errored!"
                )
            else:
                print(
                    f"Attempted to blast {len(reposNumber)} master branch in the local repo and remotely and it errored!"
                )
    print_names_and_errors(finalRepos["reposDeleteLocalAndRemote"])

    reposNumber = len(finalRepos["reposLocalProcess"]["repos"])
    repoErrorsNumber = len(finalRepos["reposLocalProcess"]["errors"])
    if len(reposNumber) > 0:
        if not len(repoErrorsNumber) > 0:
            if len(reposNumber > 1):
                print(f"{len(reposNumber)} local repos synced with blasted remotes!")
            else:
                print(f"{len(reposNumber)} local repo synced with a blasted remote!")
        elif len(reposNumber) > len(repoErrorsNumber):
            if len(repoErrorsNumber) > 1:
                print(
                    f"Attempted to sync {len(reposNumber)} local repos with blasted remotes, succeeded with {len(reposNumber) - len(repoErrorsNumber)} while {len(repoErrorsNumber)} had errors!"
                )
            else:
                print(
                    f"Attempted to sync {len(reposNumber)} local repos with blasted remotes, succeeded with {len(reposNumber) - len(repoErrorsNumber)} while {len(repoErrorsNumber)} had an error!"
                )
        else:
            if len(reposNumber) > 1:
                print(
                    f"Attempted to sync {len(reposNumber)} local repos with blasted remotes, all errored!"
                )
            else:
                print(
                    f"Attempted to sync {len(reposNumber)} local repo with a blasted remote and it errored!"
                )
    print_names_and_errors(finalRepos["reposLocalProcess"])

    reposNumber = len(finalRepos["reposMvThirdToTargetLocal"]["repos"])
    repoErrorsNumber = len(finalRepos["reposMvThirdToTargetLocal"]["errors"])
    if len(reposNumber) > 0:
        if not len(repoErrorsNumber) > 0:
            if len(reposNumber > 1):
                print(f"{len(reposNumber)} branches renamed from local repos!")
            else:
                print(f"{len(reposNumber)} branch renamed from the local repo!")
        elif len(reposNumber) > len(repoErrorsNumber):
            if len(repoErrorsNumber) > 1:
                print(
                    f"Attempted to rename {len(reposNumber)} branches from local repos, succeeded with {len(reposNumber) - len(repoErrorsNumber)} while {len(repoErrorsNumber)} had errors!"
                )
            else:
                print(
                    f"Attempted to rename {len(reposNumber)} branches from local repos, succeeded with {len(reposNumber) - len(repoErrorsNumber)} while {len(repoErrorsNumber)} had an error!"
                )
        else:
            if len(reposNumber) > 1:
                print(
                    f"Attempted to rename {len(reposNumber)} branches from local repos, all errored!"
                )
            else:
                print(
                    f"Attempted to rename {len(reposNumber)} branches from the local repo and it errored!"
                )
    print_names_and_errors(finalRepos["reposMvThirdToTargetLocal"])

    reposNumber = len(finalRepos["reposMvThirdToTargetClone"]["repos"])
    repoErrorsNumber = len(finalRepos["reposMvThirdToTargetClone"]["errors"])
    if len(reposNumber) > 0:
        if not len(repoErrorsNumber) > 0:
            if len(reposNumber > 1):
                print(f"{len(reposNumber)} branches renamed by cloning the repos!")
            else:
                print(f"{len(reposNumber)} branch renamed by cloning the repo!")
        elif len(reposNumber) > len(repoErrorsNumber):
            if len(repoErrorsNumber) > 1:
                print(
                    f"Attempted to rename {len(reposNumber)} branches by cloning the repos, succeeded with {len(reposNumber) - len(repoErrorsNumber)} while {len(repoErrorsNumber)} had errors!"
                )
            else:
                print(
                    f"Attempted to rename {len(reposNumber)} branches by cloning the repos, succeeded with {len(reposNumber) - len(repoErrorsNumber)} while {len(repoErrorsNumber)} had an error!"
                )
        else:
            if len(reposNumber) > 1:
                print(
                    f"Attempted to rename {len(reposNumber)} branches by cloning the repos, all errored!"
                )
            else:
                print(
                    f"Attempted to rename {len(reposNumber)} branch by cloning the repo and it errored!"
                )
    print_names_and_errors(finalRepos["reposMvThirdToTargetClone"])

    reposNumber = len(finalRepos["reposMvThirdToTargetAndBlastLocalMaster"]["repos"])
    repoErrorsNumber = len(
        finalRepos["reposMvThirdToTargetAndBlastLocalMaster"]["errors"]
    )
    if len(reposNumber) > 0:
        if not len(repoErrorsNumber) > 0:
            if len(reposNumber > 1):
                print(
                    f"{len(reposNumber)} branches renamed from local repos and local master branches deleted!"
                )
            else:
                print(
                    f"{len(reposNumber)} branch renamed from the local repo and the local master branch deleted!"
                )
        elif len(reposNumber) > len(repoErrorsNumber):
            if len(repoErrorsNumber) > 1:
                print(
                    f"Attempted to rename {len(reposNumber)} branches from local repos and delete the local master branches, succeeded with {len(reposNumber) - len(repoErrorsNumber)} while {len(repoErrorsNumber)} had errors!"
                )
            else:
                print(
                    f"Attempted to rename {len(reposNumber)} branches from local repos and delete the local master branches, succeeded with {len(reposNumber) - len(repoErrorsNumber)} while {len(repoErrorsNumber)} had an error!"
                )
        else:
            if len(reposNumber) > 1:
                print(
                    f"Attempted to rename {len(reposNumber)} branches from local repos and delete the local master branches, all errored!"
                )
            else:
                print(
                    f"Attempted to rename {len(reposNumber)} branch from a local repo and delete the local master branch and it errored!"
                )
    print_names_and_errors(finalRepos["reposMvThirdToTargetAndBlastLocalMaster"])

    reposNumber = len(finalRepos["reposPathUnclear"])
    if len(reposNumber) > 0:
        if len(reposNumber > 1):
            print(
                f"{len(reposNumber)} repos weren't acted on because the path for action was unclear!"
            )
        else:
            print(
                f"{len(reposNumber)} repo wasn't acted on because the path for action was unclear!"
            )
    print_names_and_errors(finalRepos["reposPathUnclear"])

    reposNumber = len(finalRepos["reposFolderError"])
    if len(reposNumber) > 0:
        if len(reposNumber > 1):
            print(
                f"{len(reposNumber)} repos weren't acted on because there was a local folder that possibly isn't git repo, error opening .git/config!"
            )
        else:
            print(
                f"{len(reposNumber)} repo wasn't acted on because there was a local folder that possibly isn't git repo, error opening .git/config!"
            )
    print_names_and_errors(finalRepos["reposFolderError"])

    reposNumber = len(finalRepos["reposAlreadyBlasted"])
    if len(reposNumber) > 0:
        if len(reposNumber > 1):
            print(f"{len(reposNumber)} repos were already blasted!")
        else:
            print(f"{len(reposNumber)} repo was already blasted!")
    print_names_and_errors(finalRepos["reposAlreadyBlasted"])

    if clonesRmAttempted:
        if reposCloneDeletionError:
            print("There was an error deleting the cloned repos!")
        else:
            print("Cloned repos deleted!")

    if gitNew:
        if gitNewError:
            print("There was an error creating the git alias!")
        else:
            print("Git alias `git new` created!")


def denoument():
    print("Thank you for using master-blaster!\n")
    print("Check the log file at ./info.log for details!")
