import logging
import os
from pathlib import Path
import questionary
from vendor.lib.actions.shell import get_local_token
from vendor.lib.utils import states


def intro():
    """Print the license, intro blurb, and token blurb!"""
    licenseText = """
      master-blaster: batch rename primary branches of git repos
      and update the associated default branches on GitHub.
      Copyright (C) 2021  Gareth Field field.gareth@gmail.com

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

      ----------------------------------------------------------------------"""
    print(licenseText)

    introText = """
      Welcome to master-blaster! This program batch renames the primary
      branches for git repos and updates the 'default' branch on GitHub.
    """
    print(introText)

    print(
        """
      Log file to be found at ./info.log!"""
    )

    tokenExplanation = """
      Also, GitHub is deprecating password-based token generation! This is great for
      security, it just means you're going to have to go to GitHub.com and
      come back with an access token to run the program, and it's a couple of steps,
      still faster than doing each manually if you have a bunch of repos, though.
      Thank you!\n"""
    print(tokenExplanation)


def get_username(testing):
    """Get the GitHub username and return it."""
    usernamePrompt = "First, please enter your GitHub username!"

    username = ""
    while True:
        username = questionary.text(usernamePrompt).ask()
        if username == "":
            print("GitHub username blank: Please try again!\n")
            continue
        if len(username) >= 40:
            print("GitHub usernames are 39 chars or less: please try again!\n")
            continue
        usernameConfirmed = questionary.confirm(f"Confirm username: {username}").ask()
        if usernameConfirmed == False:
            print("Thank you for retrying!\n")
            continue
        if usernameConfirmed:
            if not testing:
                logging.info(f"Username: {username}")
                break
            if testing:
                break

    if testing:
        username = "montymcblaster88"
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
    print("\n")
    return token


def repo_types_blurb():
    """Explain all repos, owner, public/private."""
    print(
        """
      Currently the only supported set of repos is all repos
      user is owner of, public and private.\n"""
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
    print("\n")
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
            print("\n")
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
                print("\n")
                if customRepoNameConfirmed:
                    repo["targetName"] = repoNameResponse
                    logging.info(
                        f"Primary branch name for {repo['htmlUrl']}: {repoNameResponse}"
                    )
                    targetNameConfirmed = True
    print("\n")
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
    print("\n")
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
        print("\n")
        if customLocalDirectoryResponse == "":
            confirmResetToHomeResponse = questionary.confirm(
                confirmResetToHomePrompt
            ).ask()
            print("\n")
            if confirmResetToHomeResponse:
                localDirectory = Path.home()
                localDirectoryConfirmed = True
        else:
            if os.path.isdir(customLocalDirectoryResponse):
                confirmCustomLocalDirectoryResponse = questionary.confirm(
                    custom_local_directory_confirm_prompt(customLocalDirectoryResponse)
                ).ask()
                print("\n")
                if confirmCustomLocalDirectoryResponse:
                    localDirectory = customLocalDirectoryResponse
                    localDirectoryConfirmed = True
            else:
                print(
                    f"Error! Directory not showing as valid: {customLocalDirectoryResponse}"
                )
    if testing:
        localDirectory = f"{Path.home()}/Code/monty"
    logging.info(f"Local directory to search: {localDirectory}")
    return localDirectory


def get_remove_clones(testing):
    confirmRemoveClonesPrompt = """
      Remove newly cloned repositories after process complete? Defaults to yes.
    """
    confirmRemoveClones = questionary.confirm(confirmRemoveClonesPrompt).ask()
    print("\n")
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
    print("\n")
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
    #      gitUrl
    #      sshUrl
    #      name
    #      ownerLogin
    #      targetName
    #      [status] # errors, at this point
    #      [localPath]
    #      [currentBranch]
    #      hasMaster
    #      hasTarget
    #      [localHasMaster]
    #      [localHasTarget]
    #      [[localHasThird]]

    # >> These matter:
    #      [status] # errors, at this point
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
    # *     "local repo but not git folder" or git branch failed when
    # *     checking local repos, which hopefully we don't see, but hey.
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

    # * This is like the sorting hat, but for git repositories:
    for repo in repos:
        try:
            if (
                states["multipleLocals"] in repo["status"]
                or states["multipleRemotes"] in repo["status"]
                or states["rejectedResponse"] in repo["status"]
            ):
                continue
        except KeyError:
            repo["status"] = []

        if not repo["hasTarget"] and not repo["hasMaster"]:
            if repo.get("localPath"):
                if (
                    repo["localHasMaster"]
                    and not repo["localHasTarget"]
                    and repo["localHasThird"]
                ):
                    repo["status"].append(states["mvThirdToTarget"])
                    repo["status"].append(states["deleteMaster"])
                    repo["pending"] = ["moveThird", "deleteMaster"]
                    continue
                if (
                    not repo["localHasMaster"]
                    and not repo["localHasTarget"]
                    and repo["localHasThird"]
                ):
                    repo["status"].append(states["mvThirdToTarget"])
                    repo["pending"] = ["moveThird"]
                    continue
            else:
                repo["status"].append(states["mvThirdToTarget"])
                repo["pending"] = ["moveThird"]
                continue
        if repo["default"] != repo["targetName"] and repo["default"] != "master":
            repo["status"].append(states["pathUnclear"])
            continue
        if (
            repo["hasTarget"]
            and repo["hasMaster"]
            and repo["default"] == repo["targetName"]
        ):
            if repo.get("localPath"):
                if repo["localHasTarget"] and repo["localHasMaster"]:
                    repo["status"].append(states["deleteMaster"])
                    repo["pending"] = ["deleteMaster"]
                    continue
                if not repo["localHasTarget"] and repo["localHasMaster"]:
                    repo["status"].append(states["deleteMaster"])
                    repo["pending"] = ["deleteMaster"]
                    continue
                repo["status"].append(states["pathUnclear"])
                continue
            repo["status"].append(states["deleteMaster"])
            repo["pending"] = ["deleteMaster"]
            continue
        if repo["hasMaster"] and not repo["hasTarget"] and repo["default"] == "master":
            if repo.get("localPath"):
                if repo["localHasMaster"] and not repo["localHasTarget"]:
                    repo["status"].append(states["remoteProcess"])
                    continue
                repo["status"].append(states["pathUnclear"])
                continue
            repo["status"].append(states["remoteProcess"])
            continue
        if (
            repo["hasTarget"]
            and not repo["hasMaster"]
            and repo["default"] == repo["targetName"]
        ):
            if repo.get("localPath"):
                if repo["localHasMaster"] and repo["localHasTarget"]:
                    repo["status"].append(states["deleteMaster"])
                    repo["pending"] = ["deleteMaster"]
                    continue
                if repo["localHasTarget"] and not repo["localHasMaster"]:
                    repo["status"].append(states["alreadyBlasted"])
                    continue
                if not repo["localHasTarget"] and repo["localHasMaster"]:
                    repo["status"].append(states["localUpdateProcess"])
                    repo["pending"] = ["localUpdateProcess"]
                    continue
                repo["status"].append(states["pathUnclear"])
                continue
            repo["status"].append(states["alreadyBlasted"])
            continue
        repo["status"].append(states["pathUnclear"])

    for repo in repos:
        if (
            states["multipleLocals"] in repo["status"]
            or states["multipleRemotes"] in repo["status"]
            or states["rejectedResponse"] in repo["status"]
        ):
            continue
        try:
            if repo.get("pending"):
                logging.info(
                    f"{repo['name']} initial status(es) determined: {' '.join(repo['status'])} (Pending.)"
                )
        except KeyError:
            logging.info(
                f"{repo['name']} initial status(es) determined: {' '.join(repo['status'])}"
            )

    updates = False

    reposMvThirdToTarget = [
        repo["name"] for repo in repos if states["mvThirdToTarget"] in repo["status"]
    ]
    if len(reposMvThirdToTarget) > 0:
        if len(reposMvThirdToTarget) > 1:
            print("The following repos have a third name for their primary branch:")
        else:
            print("The following repo has a third name for its primary branch:")
        for repoName in reposMvThirdToTarget:
            print(repoName)
        decision = False
        if len(reposMvThirdToTarget) > 1:
            decision = questionary.confirm(
                "Do you want to rename these branches?"
            ).ask()
        else:
            decision = questionary.confirm("Do you want to rename this branch?").ask()
        if decision:
            updates = True
            for repoName in reposMvThirdToTarget:
                for repo in repos:
                    if repoName == repo["name"]:
                        repo["pending"].remove("moveThird")
                        repo["updated"] = True
        else:
            for repoName in reposMvThirdToTarget:
                for repo in repos:
                    if repoName == repo["name"]:
                        repo["status"].remove[states["mvThirdToTarget"]]

    reposDeleteMaster = [
        repo["name"] for repo in repos if states["deleteMaster"] in repo["status"]
    ]
    if len(reposDeleteMaster) > 0:
        if len(reposDeleteMaster) > 1:
            print("The following repos have master branches that can be deleted:")
        else:
            print("The following repo has a master branch that can be deleted:")
        for repoName in reposDeleteMaster:
            print(repoName)
        decision = False
        if len(reposDeleteMaster) > 1:
            decision = questionary.confirm(
                "Do you want to delete these branches?"
            ).ask()
        else:
            decision = questionary.confirm("Do you want to delete this branch?").ask()
        if decision:
            updates = True
            for repoName in reposDeleteMaster:
                for repo in repos:
                    if repoName == repo["name"]:
                        repo["pending"].remove("deleteMaster")
                        repo["updated"] = True
        else:
            for repoName in reposDeleteMaster:
                for repo in repos:
                    if repoName == repo["name"]:
                        repo["status"].remove(states["deleteMaster"])

    reposlocalUpdateProcess = [
        repo["name"] for repo in repos if states["localUpdateProcess"] in repo["status"]
    ]
    if len(reposlocalUpdateProcess) > 0:
        if len(reposlocalUpdateProcess) > 1:
            print("The following repos have local repos that can be updated:")
        else:
            print("The following repo has a local repo that can be updated:")
        for repoName in reposlocalUpdateProcess:
            print(repoName)
        decision = False
        if len(reposlocalUpdateProcess) > 1:
            decision = questionary.confirm("Do you want to update these repos?").ask()
        else:
            decision = questionary.confirm("Do you want to update this repo?").ask()
        if decision:
            updates = True
            for repoName in reposlocalUpdateProcess:
                for repo in repos:
                    if repoName == repo["name"]:
                        repo["pending"].remove("localUpdateProcess")
                        repo["updated"] = True
        else:
            for repoName in reposlocalUpdateProcess:
                for repo in repos:
                    if repoName == repo["name"]:
                        repo["status"].remove(states["localUpdateProcess"])

    if updates:
        for repo in repos:
            try:
                if repo["updated"]:
                    logging.info(
                        f"{repo['name']} status(es) has been updated to: {' '.join(repo['status'])}"
                    )
            except KeyError:
                pass
    # print("check_names")
    # print(repos)
    return repos


def print_names_and_errors(repos, errorsPossiblyPresent=False):
    """Print out the names of successes, if present, then errors, if present,
    or the repos otherwise."""
    reposNumber = len(repos)
    if errorsPossiblyPresent:
        repoErrorsNumber = len([repo for repo in repos if repo.get("error")])
        if reposNumber > repoErrorsNumber:
            print(f"Successes: {reposNumber - repoErrorsNumber}")
            if repoErrorsNumber > 0:
                for repo in repos:
                    error = False
                    for errorRepo in [repo for repo in repos if repo.get("error")]:
                        if repo["name"] == errorRepo["name"]:
                            error = True
                    if not error:
                        print(repo["name"])
                print("\n")
                print(f"Errors: {repoErrorsNumber}")
                for errorRepo in [repo for repo in repos if repo.get("error")]:
                    print(errorRepo["name"])
                print("\n")
            else:
                for repo in repos:
                    print(repo["name"])
                print("\n")
        else:
            print(f"Errors: {repoErrorsNumber}")
            for errorRepo in [repo for repo in repos if repo.get("error")]:
                print(errorRepo["name"])
            print("\n")
    else:
        print(f"Repos: {reposNumber}")
        for repo in repos:
            print(repo["name"])
        print("\n")


# TODO pending includes strings "moveThird", "deleteMaster", and/or "local"
# alreadyBlasteds = [
#     repo for repo in repos if states["alreadyBlasted"] in repo["status"]
# ]
# multipleLocalRepos = [
#     repo for repo in repos if states["multipleLocals"] in repo["status"]
# ]
# multipleRemoteRepos = [
#     repo for repo in repos if states["multipleRemotes"] in repo["status"]
# ]
# gitBranchErrors = [
#     repo for repo in repos if states["gitBranchError"] in repo["status"]
# ]
# rejectedResponses = [
#     repo for repo in repos if states["rejectedResponse"] in repo["status"]
# ]
# pathUnclears = [repo for repo in repos if states["pathUnclear"] in repo["status"]]


def report_on(
    repos, finalRepos, clonesRmAttempted, reposCloneDeletionError, gitNew, gitNewError
):
    """What happened?"""
    print("\nProcess complete!\n")

    reposNumber = len(finalRepos["mvThirdToTargetLocalRepos"])
    repoErrorsNumber = len(
        [repo for repo in finalRepos["mvThirdToTargetLocalRepos"] if repo.get("error")]
    )
    if reposNumber > 0:
        if not repoErrorsNumber > 0:
            if reposNumber > 1:
                print(
                    f"Primary branches updated to target name from local repos for {reposNumber} repos!\n"
                )
            else:
                print(
                    f"Primary branch updated to target name from local repo for {reposNumber} repo!\n"
                )
        elif reposNumber > repoErrorsNumber:
            if repoErrorsNumber > 1:
                print(
                    f"Attempted to update primary branches of {reposNumber} repos from local repos, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had errors!\n"
                )
            else:
                print(
                    f"Attempted to update primary branches of {reposNumber} repo from local repo, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had an error!\n"
                )
        else:
            if reposNumber > 1:
                print(
                    f"Attempted to update primary branches of {reposNumber} repos from local repos, all errored!\n"
                )
            else:
                print(
                    f"Attempted to update primary branch of {reposNumber} repo from the local repo and it errored!\n"
                )
    if reposNumber > 0:
        print_names_and_errors(
            finalRepos["mvThirdToTargetLocalRepos"], errorsPossiblyPresent=True
        )

    reposNumber = len(finalRepos["mvThirdToTargetCloneRepos"])
    repoErrorsNumber = len(
        [repo for repo in finalRepos["mvThirdToTargetCloneRepos"] if repo.get("error")]
    )
    if reposNumber > 0:
        if not repoErrorsNumber > 0:
            if reposNumber > 1:
                print(
                    f"Primary branches updated to target name from cloned repos for {reposNumber} repos!\n"
                )
            else:
                print(
                    f"Primary branch updated to target name from cloned repo for {reposNumber} repo!\n"
                )
        elif reposNumber > repoErrorsNumber:
            if repoErrorsNumber > 1:
                print(
                    f"Attempted to update primary branches of {reposNumber} repos from cloned repos, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had errors!\n"
                )
            else:
                print(
                    f"Attempted to update primary branches of {reposNumber} repo from cloned repo, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had an error!\n"
                )
        else:
            if reposNumber > 1:
                print(
                    f"Attempted to update primary branches of {reposNumber} repos from cloned repos, all errored!\n"
                )
            else:
                print(
                    f"Attempted to update primary branch of {reposNumber} repo from the cloned repo and it errored!\n"
                )
    if reposNumber > 0:
        print_names_and_errors(
            finalRepos["mvThirdToTargetCloneRepos"], errorsPossiblyPresent=True
        )

    reposNumber = len(finalRepos["mvThirdToTargetAndDeleteRemoteMasterLocalRepos"])
    repoErrorsNumber = len(
        [
            repo
            for repo in finalRepos["mvThirdToTargetAndDeleteRemoteMasterLocalRepos"]
            if repo.get("error")
        ]
    )
    if reposNumber > 0:
        if not repoErrorsNumber > 0:
            if reposNumber > 1:
                print(
                    f"Primary branches updated to target name and remote master branch deleted from local repos for {reposNumber} repos!\n"
                )
            else:
                print(
                    f"Primary branch updated to target name and remote master branch deleted from local repo for {reposNumber} repo!\n"
                )
        elif reposNumber > repoErrorsNumber:
            if repoErrorsNumber > 1:
                print(
                    f"Attempted to update primary branches and delete remote master branches of {reposNumber} repos from local repos, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had errors!\n"
                )
            else:
                print(
                    f"Attempted to update primary branches and delete remote master branch of {reposNumber} repo from local repo, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had an error!\n"
                )
        else:
            if reposNumber > 1:
                print(
                    f"Attempted to update primary branches and delete remote master branches of {reposNumber} repos from local repos, all errored!\n"
                )
            else:
                print(
                    f"Attempted to update primary branch and delete remote master branch of {reposNumber} repo from the local repo and it errored!\n"
                )
    if reposNumber > 0:
        print_names_and_errors(
            finalRepos["mvThirdToTargetAndDeleteRemoteMasterLocalRepos"],
            errorsPossiblyPresent=True,
        )

    reposNumber = len(finalRepos["mvThirdToTargetAndDeleteRemoteMasterCloneRepos"])
    repoErrorsNumber = len(
        [
            repo
            for repo in finalRepos["mvThirdToTargetAndDeleteRemoteMasterCloneRepos"]
            if repo.get("error")
        ]
    )
    if reposNumber > 0:
        if not repoErrorsNumber > 0:
            if reposNumber > 1:
                print(
                    f"Primary branches updated to target name and remote master branch deleted from cloned repos for {reposNumber} repos!\n"
                )
            else:
                print(
                    f"Primary branch updated to target name and remote master branch deleted from cloned repo for {reposNumber} repo!\n"
                )
        elif reposNumber > repoErrorsNumber:
            if repoErrorsNumber > 1:
                print(
                    f"Attempted to update primary branches and delete remote master branches of {reposNumber} repos from cloned repos, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had errors!\n"
                )
            else:
                print(
                    f"Attempted to update primary branches and delete remote master branch of {reposNumber} repo from cloned repo, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had an error!\n"
                )
        else:
            if reposNumber > 1:
                print(
                    f"Attempted to update primary branches and delete remote master branches of {reposNumber} repos from cloned repos, all errored!\n"
                )
            else:
                print(
                    f"Attempted to update primary branch and delete remote master branch of {reposNumber} repo from the cloned repo and it errored!\n"
                )
    if reposNumber > 0:
        print_names_and_errors(
            finalRepos["mvThirdToTargetAndDeleteRemoteMasterCloneRepos"],
            errorsPossiblyPresent=True,
        )

    reposNumber = len(finalRepos["mvThirdToTargetAndDeleteRemoteAndLocalMasters"])
    repoErrorsNumber = len(
        [
            repo
            for repo in finalRepos["mvThirdToTargetAndDeleteRemoteAndLocalMasters"]
            if repo.get("error")
        ]
    )
    if reposNumber > 0:
        if not repoErrorsNumber > 0:
            if reposNumber > 1:
                print(
                    f"Primary branches updated to target name and remote and local master branch deleted from local repos for {reposNumber} repos!\n"
                )
            else:
                print(
                    f"Primary branch updated to target name and remote and local master branches deleted from local repo for {reposNumber} repo!\n"
                )
        elif reposNumber > repoErrorsNumber:
            if repoErrorsNumber > 1:
                print(
                    f"Attempted to update primary branches and delete remote and local master branches of {reposNumber} repos from local repos, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had errors!\n"
                )
            else:
                print(
                    f"Attempted to update primary branches and delete remote and local master branches of {reposNumber} repo from local repo, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had an error!\n"
                )
        else:
            if reposNumber > 1:
                print(
                    f"Attempted to update primary branches and delete remote and local master branches of {reposNumber} repos from local repos, all errored!\n"
                )
            else:
                print(
                    f"Attempted to update primary branch and delete remote and local master branches of {reposNumber} repo from the local repo and it errored!\n"
                )
    if reposNumber > 0:
        print_names_and_errors(
            finalRepos["mvThirdToTargetAndDeleteRemoteAndLocalMasters"],
            errorsPossiblyPresent=True,
        )

    reposNumber = len(finalRepos["mvThirdToTargetAndDeleteLocalMasters"])
    repoErrorsNumber = len(
        [
            repo
            for repo in finalRepos["mvThirdToTargetAndDeleteLocalMasters"]
            if repo.get("error")
        ]
    )
    if reposNumber > 0:
        if not repoErrorsNumber > 0:
            if reposNumber > 1:
                print(
                    f"Primary branches updated to target name and local master branch deleted from local repos for {reposNumber} repos!\n"
                )
            else:
                print(
                    f"Primary branch updated to target name and local master branch deleted from local repo for {reposNumber} repo!\n"
                )
        elif reposNumber > repoErrorsNumber:
            if repoErrorsNumber > 1:
                print(
                    f"Attempted to update primary branches and delete local master branches of {reposNumber} repos from local repos, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had errors!\n"
                )
            else:
                print(
                    f"Attempted to update primary branches and delete local master branch of {reposNumber} repo from local repo, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had an error!\n"
                )
        else:
            if reposNumber > 1:
                print(
                    f"Attempted to update primary branches and delete local master branches of {reposNumber} repos from local repos, all errored!\n"
                )
            else:
                print(
                    f"Attempted to update primary branch and delete local master branch of {reposNumber} repo from the local repo and it errored!\n"
                )
    if reposNumber > 0:
        print_names_and_errors(
            finalRepos["mvThirdToTargetAndDeleteLocalMasters"],
            errorsPossiblyPresent=True,
        )

    reposNumber = len(finalRepos["deleteRemoteMasterLocalRepos"])
    repoErrorsNumber = len(
        [
            repo
            for repo in finalRepos["deleteRemoteMasterLocalRepos"]
            if repo.get("error")
        ]
    )
    if reposNumber > 0:
        if not repoErrorsNumber > 0:
            if reposNumber > 1:
                print(
                    f"Remote master branches deleted from local repos for {reposNumber} repos!\n"
                )
            else:
                print(
                    f"Remote master branch deleted from local repo for {reposNumber} repo!\n"
                )
        elif reposNumber > repoErrorsNumber:
            if repoErrorsNumber > 1:
                print(
                    f"Attempted to delete remote master branches of {reposNumber} repos from local repos, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had errors!\n"
                )
            else:
                print(
                    f"Attempted to delete remote master branch of {reposNumber} repo from local repo, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had an error!\n"
                )
        else:
            if reposNumber > 1:
                print(
                    f"Attempted to delete remote master branches of {reposNumber} repos from local repos, all errored!\n"
                )
            else:
                print(
                    f"Attempted to delete remote master branch of {reposNumber} repo from the local repo and it errored!\n"
                )
    if reposNumber > 0:
        print_names_and_errors(
            finalRepos["deleteRemoteMasterLocalRepos"], errorsPossiblyPresent=True
        )

    reposNumber = len(finalRepos["deleteRemoteMasterCloneRepos"])
    repoErrorsNumber = len(
        [
            repo
            for repo in finalRepos["deleteRemoteMasterCloneRepos"]
            if repo.get("error")
        ]
    )
    if reposNumber > 0:
        if not repoErrorsNumber > 0:
            if reposNumber > 1:
                print(
                    f"Remote master branches deleted from cloned repos for {reposNumber} repos!\n"
                )
            else:
                print(
                    f"Remote master branch deleted from cloned repo for {reposNumber} repo!\n"
                )
        elif reposNumber > repoErrorsNumber:
            if repoErrorsNumber > 1:
                print(
                    f"Attempted to delete remote master branches of {reposNumber} repos from cloned repos, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had errors!\n"
                )
            else:
                print(
                    f"Attempted to delete remote master branch of {reposNumber} repo from cloned repo, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had an error!\n"
                )
        else:
            if reposNumber > 1:
                print(
                    f"Attempted to delete remote master branches of {reposNumber} repos from cloned repos, all errored!\n"
                )
            else:
                print(
                    f"Attempted to delete remote master branch of {reposNumber} repo from the cloned repo and it errored!\n"
                )
    if reposNumber > 0:
        print_names_and_errors(
            finalRepos["deleteRemoteMasterCloneRepos"], errorsPossiblyPresent=True
        )

    reposNumber = len(finalRepos["deleteLocalAndRemoteMasters"])
    repoErrorsNumber = len(
        [
            repo
            for repo in finalRepos["deleteLocalAndRemoteMasters"]
            if repo.get("error")
        ]
    )
    if reposNumber > 0:
        if not repoErrorsNumber > 0:
            if reposNumber > 1:
                print(
                    f"Remote and local master branches deleted from local repos for {reposNumber} repos!\n"
                )
            else:
                print(
                    f"Remote and local master branches deleted from local repo for {reposNumber} repo!\n"
                )
        elif reposNumber > repoErrorsNumber:
            if repoErrorsNumber > 1:
                print(
                    f"Attempted to delete remote and local master branches of {reposNumber} repos from local repos, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had errors!\n"
                )
            else:
                print(
                    f"Attempted to delete remote and local master branches of {reposNumber} repo from local repo, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had an error!\n"
                )
        else:
            if reposNumber > 1:
                print(
                    f"Attempted to delete remote and local master branches of {reposNumber} repos from local repos, all errored!\n"
                )
            else:
                print(
                    f"Attempted to delete remote and local master branches of {reposNumber} repo from the local repo and it errored!\n"
                )
    if reposNumber > 0:
        print_names_and_errors(
            finalRepos["deleteLocalAndRemoteMasters"], errorsPossiblyPresent=True
        )

    reposNumber = len(finalRepos["deleteLocalMasters"])
    repoErrorsNumber = len(
        [repo for repo in finalRepos["deleteLocalMasters"] if repo.get("error")]
    )
    if reposNumber > 0:
        if not repoErrorsNumber > 0:
            if reposNumber > 1:
                print(
                    f"Local master branches deleted from local repos for {reposNumber} repos!\n"
                )
            else:
                print(
                    f"Local master branch deleted from local repo for {reposNumber} repo!\n"
                )
        elif reposNumber > repoErrorsNumber:
            if repoErrorsNumber > 1:
                print(
                    f"Attempted to delete local master branches of {reposNumber} repos from local repos, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had errors!\n"
                )
            else:
                print(
                    f"Attempted to delete local master branch of {reposNumber} repo from local repo, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had an error!\n"
                )
        else:
            if reposNumber > 1:
                print(
                    f"Attempted to delete local master branches of {reposNumber} repos from local repos, all errored!\n"
                )
            else:
                print(
                    f"Attempted to delete local master branch of {reposNumber} repo from the local repo and it errored!\n"
                )
    if reposNumber > 0:
        print_names_and_errors(
            finalRepos["deleteLocalMasters"], errorsPossiblyPresent=True
        )

    reposNumber = len(finalRepos["localUpdates"])
    repoErrorsNumber = len(
        [repo for repo in finalRepos["localUpdates"] if repo.get("error")]
    )
    if reposNumber > 0:
        if not repoErrorsNumber > 0:
            if reposNumber > 1:
                print(
                    f"Local repo synced with remote repo which has already had master blasted for {reposNumber} repos!\n"
                )
            else:
                print(
                    f"Local repo synced with remote repo which has already had master blasted for {reposNumber} repo!\n"
                )
        elif reposNumber > repoErrorsNumber:
            if repoErrorsNumber > 1:
                print(
                    f"Attempted to sync local repo with remote that has already been blasted for {reposNumber} repos, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had errors!\n"
                )
            else:
                print(
                    f"Attempted to sync local repo with remote that has already been blasted for {reposNumber} repos, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had an error!\n"
                )
        else:
            if reposNumber > 1:
                print(
                    f"Attempted to sync local repo with remote that has already been blasted for {reposNumber} repos, all errored!\n"
                )
            else:
                print(
                    f"Attempted to sync local repo with remote that has already been blasted for {reposNumber} repo, and it errored!\n"
                )
    if reposNumber > 0:
        print_names_and_errors(finalRepos["localUpdates"], errorsPossiblyPresent=True)

    reposNumber = len(finalRepos["remoteProcessLocalRepos"])
    repoErrorsNumber = len(
        [repo for repo in finalRepos["remoteProcessLocalRepos"] if repo.get("error")]
    )
    if reposNumber > 0:
        if not repoErrorsNumber > 0:
            if reposNumber > 1:
                print(f"Master blasted from local repos for {reposNumber} repos!\n")
            else:
                print(f"Master blasted from local repo for {reposNumber} repo!\n")
        elif reposNumber > repoErrorsNumber:
            if repoErrorsNumber > 1:
                print(
                    f"Attempted to blast masters for {reposNumber} repos from local repos, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had errors!\n"
                )
            else:
                print(
                    f"Attempted to blast master for {reposNumber} repo from local repo, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had an error!\n"
                )
        else:
            if reposNumber > 1:
                print(
                    f"Attempted to blast masters for {reposNumber} repos from local repos, all errored!\n"
                )
            else:
                print(
                    f"Attempted to blast master for {reposNumber} repo from the local repo and it errored!\n"
                )
    if reposNumber > 0:
        print_names_and_errors(
            finalRepos["remoteProcessLocalRepos"], errorsPossiblyPresent=True
        )

    reposNumber = len(finalRepos["remoteProcessCloneRepos"])
    repoErrorsNumber = len(
        [repo for repo in finalRepos["remoteProcessCloneRepos"] if repo.get("error")]
    )
    if reposNumber > 0:
        if not repoErrorsNumber > 0:
            if reposNumber > 1:
                print(f"Master blasted from cloned repos for {reposNumber} repos!\n")
            else:
                print(f"Master blasted from cloned repo for {reposNumber} repo!\n")
        elif reposNumber > repoErrorsNumber:
            if repoErrorsNumber > 1:
                print(
                    f"Attempted to blast masters for {reposNumber} repos from cloned repos, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had errors!\n"
                )
            else:
                print(
                    f"Attempted to blast master for {reposNumber} repo from cloned repo, succeeded with {reposNumber - repoErrorsNumber} while {repoErrorsNumber} had an error!\n"
                )
        else:
            if reposNumber > 1:
                print(
                    f"Attempted to blast masters for {reposNumber} repos from cloned repos, all errored!\n"
                )
            else:
                print(
                    f"Attempted to blast master for {reposNumber} repo from the cloned repo and it errored!\n"
                )
    if reposNumber > 0:
        print_names_and_errors(
            finalRepos["remoteProcessCloneRepos"], errorsPossiblyPresent=True
        )

    reposNumber = len(
        [repo for repo in repos if states["alreadyBlasted"] in repo["status"]]
    )
    if reposNumber > 0:
        if reposNumber > 1:
            print(f"{reposNumber} repos were already blasted!\n")
        else:
            print(f"{reposNumber} repo were already blasted!\n")
    if reposNumber > 0:
        print_names_and_errors(
            [repo for repo in repos if states["alreadyBlasted"] in repo["status"]]
        )

    reposNumber = len(
        [repo for repo in repos if states["multipleLocals"] in repo["status"]]
    )
    if reposNumber > 0:
        if reposNumber > 1:
            print(
                f"{reposNumber} repos weren't acted on because there were multiple local repos!\n"
            )
        else:
            print(
                f"{reposNumber} repo wasn't acted on because there were multiple local repos!\n"
            )
    if reposNumber > 0:
        print_names_and_errors(
            [repo for repo in repos if states["multipleLocals"] in repo["status"]]
        )

    reposNumber = len(
        [repo for repo in repos if states["multipleRemotes"] in repo["status"]]
    )
    if reposNumber > 0:
        if reposNumber > 1:
            print(
                f"{reposNumber} repos weren't acted on because there were multiple remotes in the\n.git/config files! That's out of scope for this version of `master-blaster`.\n"
            )
        else:
            print(
                f"{reposNumber} repo wasn't acted on because there were multiple remotes in the\n.git/config file! That's out of scope for this version of `master-blaster`.\n"
            )
    if reposNumber > 0:
        print_names_and_errors(
            [repo for repo in repos if states["multipleRemotes"] in repo["status"]]
        )

    reposNumber = len(
        [repo for repo in repos if states["gitBranchError"] in repo["status"]]
    )
    if reposNumber > 0:
        if reposNumber > 1:
            print(
                f"{reposNumber} repos weren't acted on because there was an error running\n`git branch` on them!\n"
            )
        else:
            print(
                f"{reposNumber} repo wasn't acted on because there was an error running\n`git branch` on it!\n"
            )
    if reposNumber > 0:
        print_names_and_errors(
            [repo for repo in repos if states["gitBranchError"] in repo["status"]]
        )

    reposNumber = len(
        [repo for repo in repos if states["rejectedResponse"] in repo["status"]]
    )
    if reposNumber > 0:
        if reposNumber > 1:
            print(
                f"{reposNumber} repos weren't acted on because there was an error with the responses from the GitHub API!\n"
            )
        else:
            print(
                f"{reposNumber} repo wasn't acted on because there was an error with the response from the GitHub API!\n"
            )
    if reposNumber > 0:
        print_names_and_errors(
            [repo for repo in repos if states["rejectedResponse"] in repo["status"]]
        )

    reposNumber = len(
        [repo for repo in repos if states["pathUnclear"] in repo["status"]]
    )
    if reposNumber > 0:
        if reposNumber > 1:
            print(
                f"{reposNumber} repos weren't acted on because the path for action was unclear!\n"
            )
        else:
            print(
                f"{reposNumber} repo wasn't acted on because the path for action was unclear!\n"
            )
    if reposNumber > 0:
        print_names_and_errors(
            [repo for repo in repos if states["pathUnclear"] in repo["status"]]
        )

    if clonesRmAttempted:
        if reposCloneDeletionError != "":
            print(f"There was an error deleting the cloned repos!\n")
        else:
            print("Cloned repos deleted!\n")

    if gitNew:
        if gitNewError:
            print(
                f"Error adding the git alias `git new` failed! You can run `git config --global alias.new '!git init && git symbolic-ref HEAD refs/heads/{finalRepos['reposRemoteProcessLocal']['repos'][0]['targetname']}` to try again!\n"
            )
        else:
            print("Git alias `git new` set (or re-set.)\n")


def denoument():
    print("Check the log file at ./info.log for details.\n")
    print("Thank you for using master-blaster!\n")
