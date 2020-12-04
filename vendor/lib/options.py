from vendor.lib.actions.shell import getLocalRepos
from vendor.lib.actions.shell import processLogger
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
        repo["primaryBranchName"] = name
    return repos


def checkBranches(username, token, repos, localRepos):
    """Catch and categorize naming errors locally and on remote repos."""

    localRepoUrls = None
    if localRepos:
        localRepoUrls = [localRepo["url"] for localRepo in localRepos]

    # * ``` Placeholder variables for groups of checked repos! ``` * #
    # I don't like this. #
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
            repo[
                "status"
            ] = "error: remote has neither master nor new primary branch name"
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

    # * ``` Check all the repos! (And prepare any locals for the check!) ``` * #
    if localRepos:
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


def wizard(data, testing):
    """Gather naming mode, name or names, catch errors, use local directories, starting local directory, removal of cloned repos, and git new alias."""
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
    localRepos = getLocalRepos(repos, localDirectory)
    removeClones = getRemoveClones(testing)
    gitNew = getGitNew(namingMode, name, testing)

    repos = checkBranches(username, token, repos, localRepos)

    return (
        username,
        token,
        repos,
        localDirectory,
        localRepos,
        removeClones,
        gitNew,
    )
