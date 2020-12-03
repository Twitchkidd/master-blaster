from vendor.lib.reporting import repoTypesBlurb
from vendor.lib.reporting import getNamingMode
from vendor.lib.reporting import getCustomName
from vendor.lib.reporting import getCustomNames


# options #
# * When the user gets a personal access token, get the options. * #

def applyName(name, repos):
    for repo in repos:
        repo["primaryBranchName"] = name
    return repos


def checkBranches(🤣):
    """Catch low-hanging fruit errors like no main or master on remote.
    Collect them for presentation in groups, though, no one-by-one nonsense."""


def wizard(username, token, repos):
    """Gather naming mode, name or names, catch errors, use local directories, starting local directory, removal of cloned repos, and git new alias."""
    reposCopy = repos
    # * Report repository types blurb. * #
    repoTypesBlurb()
    # * Placeholder for naming mode. * #
    namingMode = ""
    # * Placeholder for name. * #
    name = ""
    # * Variables for the naming mode choices (questionary returns string of answer) * #
    main = "All primary branches renamed to 'main'."
    custom = "Choose name for all primary branches renamed to. "
    perRepo = "Choose a name for the primary branch for each repo."
    # * Get naming mode. * #
    namingMode = getNamingMode(main, custom, perRepo)
    # * If default, assign it. * #
    if namingMode == main:
        name = "main"
    # * If custom, get and confirm custom. * #
    if namingMode == custom:
        name = getCustomName()
    # * If interactive, get the names and apply, otherwise apply name. * #
    if namingMode == perRepo:
        reposCopy = getCustomNames(repos)
    else:
        reposCopy = applyName(name, repos)
    # * Check repos based on options for validity. * #


    Placeholder for local directory.
    # reporting #
    Local directories prompt.

    If yes, which local directory or default?

    Test that local directory is real.

    Test all the repos and names again.

    Placeholder for remove cloned repos.

    Ask about remove cloned repos.

    Placeholder for git new.

    Ask about git new.

    Pew Pew.
    # logging #
    Log it.

    # TODO Collect testing stuff

    Return data + naming mode, name(s), use local directory, local directory, remove cloned repos, git new.


from pathlib import Path


def sayHi():
    print("Hello!")




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
            else:
                continue
        else:
            if os.path.isdir(customLocalDirectoryResponse):
                confirmCustomLocalDirectoryResponse = questionary.confirm(
                    customLocalDirectoryConfirmPrompt(customLocalDirectoryResponse)
                ).ask()
                if confirmCustomLocalDirectoryResponse:
                    localDirectory = customLocalDirectoryResponse
                    localDirectoryConfirmed = True
                    # ! Testing! #
                    # logging.info(
                    #     f"Local directory to search: {localDirectory}")
                    pass
            else:
                print(
                    f"Error! Directory not showing as valid: {customLocalDirectoryResponse}"
                )
                continue

# ! Testing! #
localDirectory = f"{Path.home()}/Code"
logging.info(f"Local directory to search: {localDirectory}")

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

# ! Testing! #
confirmRemoveLocalDirectoriesAfter = True
logging.info(
    f"Confirm remove local directories after: {confirmRemoveLocalDirectoriesAfter}"
)

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
