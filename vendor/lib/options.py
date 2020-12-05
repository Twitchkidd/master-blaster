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
    for repo in repos:
        check(repo)

    # Repo:
    #   default
    #   htmlUrl
    #   name
    #   owner-login
    #   [error] # local folder with name, can't read .git/config
    #   [configUrl]
    #   [localPath]
    #   [currentBranch]
    #   hasMaster
    #   hasTarget
    #   [localHasMaster]
    #   [localHasTarget]

    def check(repo):
        """If the (remote, this is all remote,) repo has both, which is ahead? Anyway, you
        can't rename master main in that case. Probably rewrite that. If it doesn't have either,
        you can't rename master main either. Maybe rename default though? Then, if local has
        the name already, and a bunch of other stuff, then it's already blasted, or if a bunch
        of other stuff is a candidate for local master delete, or if the local ... we could never
        GET to the local process, wtf? Anyway, or if some stuff either local or remote process,
        or the default is something else even if it has main and master. Again for no local repos."""
        if repo["hasMaster"] and repo["hasPrimary"]:
            repo[
                "status"
            ] = "error: remote has both master branch and new primary branch name"
            reposWithErrors.append(repo)
            return None
        if not repo["hasMaster"] and not repo["hasPrimary"]:
            repo[
                "status"
            ] = "error: remote has neither master nor new primary branch name"
            reposWithErrors.append(repo)
            return None
        if repo.get("localHasTarget") != None:
            if (
                not repo["hasMaster"]
                and repo["hasPrimary"]
                and repo["default"] == repo["targetName"]
                and not repo["localHasMaster"]
                and repo["localHasTarget"]
            ):
                repo["status"] = "already blasted"
                reposAlreadyBlasted.append(repo)
                return None
            if (
                not repo["hasMaster"]
                and repo["hasPrimary"]
                and repo["default"] == repo["targetName"]
                and repo["localHasMaster"]
                and repo["localHasTarget"]
            ):
                repo["status"] = "candidate to delete local master"
                reposReadyForLocalMasterDelete.append(repo)
                return None
            if repo["localHasMaster"] and not repo["localHasTarget"]:
                if (
                    not repo["hasMaster"]
                    and repo["hasPrimary"]
                    and repo["default"] == repo["targetName"]
                ):
                    repo["status"] = "candidate for local process"
                    reposReadyForLocal.append(repo)
                    return None
                if (
                    repo["hasMaster"]
                    and not repo["hasPrimary"]
                    and repo["default"] == "master"
                ):
                    repo["status"] = "candidate for remote process"
                    reposReadyForRemote.append(repo)
                    return None
            if repo["default"] != repo["targetName"] and repo["default"] != "master":
                repo[
                    "status"
                ] = f"Primary branch neither {repo['targetName']} nor master"
                reposWithErrors.append(repo)
                return None
            repo["status"] = f"error: {repo}"
            reposWithErrors.append(repo)
            return None
        else:
            if (
                not repo["hasMaster"]
                and repo["hasPrimary"]
                and repo["default"] == repo["targetName"]
            ):
                repo["status"] = "already blasted"
                reposAlreadyBlasted.append(repo)
                return None
            if (
                repo["hasMaster"]
                and not repo["hasPrimary"]
                and repo["default"] == "master"
            ):
                repo["status"] = "candidate for remote process"
                reposReadyForRemote.append(repo)
                return None
            if repo["default"] != repo["targetName"] and repo["default"] != "master":
                repo[
                    "status"
                ] = f"Primary branch neither {repo['targetName']} nor master"
                reposWithErrors.append(repo)
                return None
        repo["status"] = f"error: {repo}"
        reposWithErrors.append(repo)
        return None

    # * ``` Placeholder variables for groups of checked repos! ``` * #
    reposAlreadyBlasted = []
    reposWithErrors = []
    reposReadyForLocal = []
    reposReadyForLocalMasterDelete = []
    # Why not remote master delete?
    reposReadyForRemote = []


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

    return username, token, repos, localDirectory, removeClones, gitNew
