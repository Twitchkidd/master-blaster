from pathlib import Path
from subprocess import Popen, PIPE

# shellActions #
# * Actions taken in the shell environment. * #


def getCurrentBranch():
    """Grab the current git branch, useful for testing."""
    # * ``` From u/merfi on SO ``` * #
    head_dir = Path().cwd() / ".git" / "HEAD"
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


# * Add the `git new` alias! * #


def runGitNew():
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


if gitNew:
    runGitNew()