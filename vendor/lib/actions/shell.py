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
        logWarning(stderr)
        return (stdout, stderr, 1)
    return (stdout, stderr, 0)


def checkLocalBranches(repos):
    """Determine presence of target/master branches, and what the default is."""
    for repo in repos:
        if repo["localPath"]:
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
    processLogger(f"cwd={directory}: git branch -m {initial} {final}", gitBranchMove)
    # TODO UPDATE THIS TO ERROR STATE HANDLING


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


# def runGitNew(name):
#     """Add the `git new` alias!"""
#     gitNewGcg = Popen(
#         [
#             "git",
#             "config",
#             "--global",
#             "alias.new",
#             f"!git init && git symbolic-ref HEAD refs/heads/{name}",
#         ],
#         stdout=PIPE,
#         stderr=PIPE,
#     )
#     gitNewGcgExitCode = processLogger(
#         f"git config --global alias.new '!git init && git symbolic-ref HEAD refs/heads/{name}'",
#         gitNewGcg,
#     )[2]
#     if gitNewGcgExitCode == 0:
#         print(f"Git alias git new: initalize git repo with HEAD ref refs/heads/{name}")
#     else:
#         print("Git alias add failed, see log file.")