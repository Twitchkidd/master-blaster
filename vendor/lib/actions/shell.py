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
        return None
    localRepos = []
    errorRepos = []
    repoNames = [repo["name"] for repo in repos]
    for root, subdirs, files in os.walk(f"{localDirectory}"):
        for subdir in subdirs:
            if any(subdir == repoName for repoName in repoNames):
                try:
                    with open(f"{root}/{subdir}/.git/config", "r") as configFile:
                        localRepos.append(
                            {
                                "url": getLocalRepoUrl(configFile).lower(),
                                "path": f"{root}/{subdir}",
                                "branch": f"{getCurrentBranch(f'{root}/{subdir}')}",
                            }
                        )
                except Exception as err:
                    errorRepos.append({"name": subdir, "error": err})
                    logWarning(f"Exception: {err}")
                    pass
    if errorRepos.len > 0:
        print(
            errorRepos.len + " errors searching for local repositories: " + errorRepos
        )
    if localRepos.len > 0:
        return localRepos
    else:
        return None


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


def runGitNew(name):
    """Add the `git new` alias!"""
    gitNewGcg = Popen(
        [
            "git",
            "config",
            "--global",
            "alias.new",
            f"!git init && git symbolic-ref HEAD refs/heads/{name}",
        ],
        stdout=PIPE,
        stderr=PIPE,
    )
    gitNewGcgExitCode = processLogger(
        f"git config --global alias.new '!git init && git symbolic-ref HEAD refs/heads/{name}'",
        gitNewGcg,
    )[2]
    if gitNewGcgExitCode == 0:
        print(f"Git alias git new: initalize git repo with HEAD ref refs/heads/{name}")
    else:
        print("Git alias add failed, see log file.")