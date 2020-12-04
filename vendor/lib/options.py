from vendor.lib.actions.shell import getLocalDirectories
from vendor.lib.reporting import repoTypesBlurb
from vendor.lib.reporting import getNamingMode
from vendor.lib.reporting import getCustomName
from vendor.lib.reporting import getCustomNames
from vendor.lib.reporting import getLocalDirectory
from vendor.lib.reporting import getRemoveLocalDirectories
from vendor.lib.reporting import getGitNew

# options #
# * When the user gets a personal access token, get the options. * #


def applyName(name, repos):
    for repo in repos:
        repo["primaryBranchName"] = name
    return repos


def checkBranches(pleaseGo):
    """Catch low-hanging fruit errors like no main or master on remote.
    Collect them for presentation in groups, though, no one-by-one nonsense."""
    print("Gotta catch em all!")
    # * Check repos based on options for validity. * #
    # * Test all the repos and names again. * #


def wizard(data, testing):
    """Gather naming mode, name or names, catch errors, use local directories, starting local directory, removal of cloned repos, and git new alias."""
    username, token, repos = data
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
        repos = getCustomNames(repos)
    else:
        repos = applyName(name, repos)

    localDirectory = getLocalDirectory(testing)

    localDirectories = getLocalDirectories(localDirectory)

    removeLocalDirectories = getRemoveLocalDirectories(testing)

    gitNew = getGitNew(namingMode, name, testing)

    repos = checkBranches(username, token, repos)

    return username, token, repos, localDirectory, removeLocalDirectories, gitNew