from vendor.lib.actions.shell import getLocalRepos
from vendor.lib.actions.shell import checkLocalBranches
from vendor.lib.actions.shell import processLogger
from vendor.lib.actions.network import checkRemoteBranches
from vendor.lib.reporting import repoTypesBlurb
from vendor.lib.reporting import getNamingMode
from vendor.lib.reporting import getCustomName
from vendor.lib.reporting import getCustomNames
from vendor.lib.reporting import getLocalDirectory
from vendor.lib.reporting import getRemoveClones
from vendor.lib.reporting import getGitNew
from vendor.lib.reporting import checkNames

# options: When the user gets a personal access token, get the options. #


def applyName(name, repos):
    for repo in repos:
        repo["targetName"] = name
    return repos


def checkBranches(username, token, repos):
    """Catch and categorize naming errors locally and on remote repos."""
    repos = checkRemoteBranches(token, repos)
    localReposPresent = False
    for repo in repos:
        if repo["localPath"]:
            localReposPresent = True
    if localReposPresent:
        repos = checkLocalBranches(repos)


def wizard(data, testing):
    """Gather naming mode, name or names, catch errors, use local directories,
    starting local directory, removal of cloned repos, and git new alias."""
    username, token, repos = data

    repoTypesBlurb()

    namingMode = ""
    name = ""

    main = "All primary branches renamed to 'main'."
    custom = "Choose name for all primary branches renamed to. "
    perRepo = "Choose a name for the primary branch for each repo."

    namingMode = getNamingMode(main, custom, perRepo)

    if namingMode == main:
        name = "main"

    if namingMode == custom:
        name = getCustomName()

    if namingMode == perRepo:
        repos = getCustomNames(repos)
    else:
        repos = applyName(name, repos)

    localDirectory = getLocalDirectory(testing)
    repos = getLocalRepos(repos, localDirectory)
    removeClones = getRemoveClones(testing)
    gitNew = getGitNew(namingMode, name, testing)
    repos = checkBranches(username, token, repos)
    repos = checkNames(repos)

    return username, token, repos, localDirectory, removeClones, gitNew
