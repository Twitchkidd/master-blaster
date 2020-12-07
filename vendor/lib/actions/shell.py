import os
from pathlib import Path
from subprocess import Popen, PIPE
from vendor.lib.logging import logInfo
from vendor.lib.logging import logWarning

# shellActions #
# * Actions taken in the shell environment. * #


def getCurrentBranch(path):
    """Grab the current git branch, useful for testing."""
    # * ``` From u/merfi on SO ``` * #
    head_dir = Path(path) / ".git" / "HEAD"
    with head_dir.open("r") as f:
        content = f.read().splitlines()
    for line in content:
        if line[0:4] == "ref:":
            return line.partition("refs/heads/")[2]


def setCurrentBranch(branch):
    """Set the current branch back to what it was, useful for testing."""
    Popen(["git", "checkout", f"{branch}"], stdout=PIPE, stderr=PIPE)


def getLocalToken():
    """Read the local file 'repo.txt' for a token, useful for testing."""
    token = ""
    with open("./repo.txt", "r") as repoF:
        token = repoF.read(40)
    return token


def getLocalRepoUrl(configFile):
    url = ""
    for line in configFile:
        if line.find("url =") != -1:
            remoteOriginUrlStart = line.find("url =")
            url = line[remoteOriginUrlStart + 6 : -1]
            return url


def getLocalRepos(repos, localDirectory):
    if localDirectory == None:
        return repos
    repoNames = [repo["name"] for repo in repos]
    for root, subdirs, files in os.walk(f"{localDirectory}"):
        for subdir in subdirs:
            if any(subdir == repoName for repoName in repoNames):
                try:
                    with open(f"{root}/{subdir}/.git/config", "r") as configFile:
                        for repo in repos:
                            if subdir == repo["name"]:
                                repo["configUrl"] = getLocalRepoUrl(configFile).lower()
                                repo["localPath"] = f"{root}/{subdir}"
                                repo[
                                    "currentBranch"
                                ] = f"{getCurrentBranch(f'{root}/{subdir}')}"
                except Exception as err:
                    for repo in repos:
                        if subdir == repo["name"]:
                            repo[
                                "status"
                            ] = "Local folder that possibly isn't git repo, error opening .git/config"
                    logWarning(f"Exception in {subdir}: {err}")
                    pass
    return repos


def processLogger(string, prc, ignoreStr="", secondIgnoreStr=""):
    """This function logs the first argument, *RUNS* the code, capturing
    stdout and stderr, logging those, possibly checks against the third
    argument, though not the fourth (?) and returns a thruple of stdout,
    stderr, and either a 0 for success or a 1 for error."""
    logInfo(string)
    stdout, stderr = prc.communicate()
    if len(stdout) > 0:
        logInfo(stdout)
    if len(stderr) > 0:
        if ignoreStr != "" and ignoreStr in stderr.decode():
            logWarning(stderr)
            logInfo("You may be able to ignore the above warning.")
            return (stdout, stderr, 0)
        if secondIgnoreStr != "" and secondIgnoreStr in stderr.decode():
            logWarning(stderr)
            logInfo("You may be able to ignore the above warning.")
            return (stdout, stderr, 0)
        logWarning(stderr)
        return (stdout, stderr, 1)
    return (stdout, stderr, 0)


def checkLocalBranches(repos):
    """Determine presence of target/master branches, and what the default is."""
    for repo in repos:
        if repo.get("localPath"):
            gitBranch = Popen(
                ["git", "branch"], cwd=repo["localPath"], stdout=PIPE, stderr=PIPE
            )
            gitBranchStdout = processLogger(
                f"cwd={repo['localPath']}: git branch", gitBranch
            )[0]
            repo["localHasMaster"] = "master" in f"{gitBranchStdout}"
            repo["localHasTarget"] = repo["targetName"] in f"{gitBranchStdout}"
            if not repo["hasTarget"] and not repo["hasMaster"]:
                repo["localHasThird"] = repo["default"] in f"{gitBranchStdout}"
    return repos


def renameBranch(initial, final, directory):
    """Renames a branch of a repo, locally."""
    gitBranchMove = Popen(
        ["git", "branch", "-m", initial, final], cwd=directory, stdout=PIPE, stderr=PIPE
    )
    loggerReturn = processLogger(
        f"cwd={directory}: git branch -m {initial} {final}", gitBranchMove
    )
    gitBranchMoveStderr = loggerReturn[1]
    gitBranchMoveExitCode = loggerReturn[2]
    if gitBranchMoveExitCode == 1:
        return gitBranchMoveStderr
    else:
        return None


def pushSettingUpstream(targetName, directory):
    """Pushes to remote, setting the upstream (remote tracking branch.)"""
    gitPushSetUpstream = Popen(
        ["git", "push", "-u", "origin", targetName],
        cwd={directory},
        stdout=PIPE,
        stderr=PIPE,
    )
    loggerReturn = processLogger(
        f"cwd={directory}: git push -u origin {targetName}",
        gitPushSetUpstream,
        ignoreStr="To",
    )
    gitPushSetUpstreamStderr = loggerReturn[1]
    gitPushSetUpstreamExitCode = loggerReturn[2]
    if gitPushSetUpstreamExitCode == 1:
        return gitPushSetUpstreamStderr
    else:
        return None


def deleteRemoteBranch(branch, directory):
    """Delete the old branch on the remote."""
    gitPushDelete = Popen(
        ["git", "push", "--delete", "origin", branch],
        cwd=directory,
        stdout=PIPE,
        stderr=PIPE,
    )
    loggerReturn = processLogger(
        f"cwd={directory}: git push --delete origin {branch}",
        gitPushDelete,
        ignoreStr="To",
    )
    gitPushDeleteStderr = loggerReturn[1]
    gitPushDeleteExitCode = loggerReturn[2]
    if gitPushDeleteExitCode == 1:
        return gitPushDeleteStderr
    else:
        return None


def mkdirIfNeedBe(username, localDirectory):
    """/master-blaster-{username} is used as a temp dir."""
    if not os.path.isdir(f"{localDirectory}/master-blaster-{username}/"):
        mkdir = Popen(
            ["mkdir", "-pv", f"{localDirectory}/master-blaster-{username}/"],
            cwd=localDirectory,
            stdout=PIPE,
            stderr=PIPE,
        )
        loggerReturn = processLogger(
            f"cwd={localDirectory}: mkdir -pv {localDirectory}/master-blaster-{username}/",
            mkdir,
        )
        mkdirStderr = loggerReturn[1]
        mkdirExitCode = loggerReturn[2]
        if mkdirExitCode == 1:
            return mkdirStderr
        else:
            return None
    else:
        return None


def cloneRepo(username, repo, localDirectory):
    """Clone the repo into the right place!"""
    gitClone = Popen(
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
    loggerReturn = processLogger(
        f"cwd={localDirectory}/master-blaster-{username}/: git clone {repo['htmlUrl']}.git ./{repo['owner-login']}/{repo['name']}",
        gitClone,
    )
    gitCloneStderr = loggerReturn[1]
    gitCloneExitCode = loggerReturn[2]
    if gitCloneExitCode == 1:
        return gitCloneStderr
    else:
        return None


def deleteLocalBranch(branch, directory):
    """Delete a local branch."""
    deleteBranch = Popen(
        ["git", "branch", "-D", branch], cwd={directory}, stdout=PIPE, stderr=PIPE
    )
    loggerReturn = processLogger(
        f"cwd={directory}: git branch -D {branch}", deleteBranch
    )
    deleteBranchStderr = loggerReturn[1]
    deleteBranchExitCode = loggerReturn[2]
    if deleteBranchExitCode == 1:
        return deleteBranchStderr
    else:
        return None


def checkout(branch, directory):
    """Check out a branch."""
    checkoutBranch = Popen(
        ["git", "checkout", branch], cwd={directory}, stdout=PIPE, stderr=PIPE
    )
    loggerReturn = processLogger(
        f"cwd={directory}: git checkout {branch}",
        checkoutBranch,
        ignoreStr="Already on",
        secondIgnoreStr="Switched to",
    )
    checkoutBranchStderr = processLogger[1]
    checkoutBranchExitCode = processLogger[2]
    if checkoutBranchExitCode == 1:
        return checkoutBranchStderr
    else:
        return None


def fetch(directory):
    gitFetch = Popen(["git", "fetch"], cwd={directory}, stdout=PIPE, stderr=PIPE)
    loggerReturn = processLogger(f"cwd={directory}: git fetch", gitFetch)
    gitFetchStderr = processLogger[1]
    gitFetchExitCode = processLogger[2]
    if gitFetchExitCode == 1:
        return gitFetchStderr
    else:
        return None


def unsetUpstream(directory):
    gitBranchUU = Popen(
        ["git", "branch", "--unset-upstream"], cwd={directory}, stdout=PIPE, stderr=PIPE
    )
    loggerReturn = processLogger(
        f"cwd={directory}: git branch --unset-upstream", gitBranchUU
    )
    gitBranchUUStderr = processLogger[1]
    gitBranchUUExitCode = processLogger[2]
    if gitBranchUUExitCode == 1:
        return gitBranchUUStderr
    else:
        return None


def setUpstream(targetName, directory):
    gitBranchSetUpstream = Popen(
        ["git", "branch", "-u", f"origin/{targetName}"],
        cwd={directory},
        stdout=PIPE,
        stderr=PIPE,
    )
    loggerReturn = processLogger(
        f"cwd={directory}: git branch -u origin/{targetName}",
        gitBranchSetUpstream,
        ignoreStr="To",
    )
    gitBranchSetUpstreamStderr = processLogger[1]
    gitBranchSetUpstreamExitCode = processLogger[2]
    if gitBranchSetUpstreamExitCode == 1:
        return gitBranchSetUpstreamStderr
    else:
        return None


def updateSymbolicRef(targetName, directory):
    updateRef = Popen(
        [
            "git",
            "symbolic-ref",
            "refs/remotes/origin/HEAD",
            f"refs/remotes/origin/{targetName}",
        ],
        cwd={directory},
        stdout=PIPE,
        stderr=PIPE,
    )
    loggerReturn = processLogger(
        f"cwd={directory}: git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/{targetName}",
        updateRef,
    )
    updateRefStderr = processLogger[1]
    updateRefExitCode = processLogger[2]
    if updateRefExitCode == 1:
        return updateRefStderr
    else:
        return None


def rmCloneFolder(username, localDirectory):
    removeDir = Popen(
        ["rm", "-dfRv", f"{localDirectory}/master-blaster-{username}/"],
        cwd={localDirectory},
        stdout=PIPE,
        stderr=PIPE,
    )
    loggerReturn = processLogger(
        f"cwd={localDirectory}: rm -dfRv {localDirectory}/master-blaster-{username}/",
        removeDir,
    )
    removeDirStderr = processLogger[1]
    removeDirExitCode = processLogger[2]
    if removeDirExitCode == 1:
        return removeDirStderr
    else:
        return None


def gitNew(targetName):
    """Add the `git new` alias."""
    gitNew = Popen(
        [
            "git",
            "config",
            "--global",
            "alias.new",
            f"!git init && git symbolic-ref HEAD refs/heads/{targetName}",
        ],
        stdout=PIPE,
        stderr=PIPE,
    )
    loggerReturn = processLogger(
        f"git config --global alias.new '!git init && git symbolic-ref HEAD refs/heads/{targetName}'",
        gitNew,
    )
    gitNewStderr = loggerReturn[1]
    gitNewExitCode = loggerReturn[2]
    if gitNewExitCode == 0:
        return gitNewStderr
    else:
        return None