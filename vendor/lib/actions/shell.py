import logging
import os
from pathlib import Path
from subprocess import Popen, PIPE
from vendor.lib.actions.shell_exceptions import GetBranchError
from vendor.lib.actions.shell_exceptions import SetBranchError
from vendor.lib.actions.shell_exceptions import RenameBranchError
from vendor.lib.actions.shell_exceptions import PushBranchRenameError
from vendor.lib.actions.shell_exceptions import DeleteRemoteError
from vendor.lib.actions.shell_exceptions import MakeDirectoryError
from vendor.lib.actions.shell_exceptions import CloneRepoError


def get_current_branch(path):
    """Grab the current git branch, useful for testing.

    Credit:
        Mostly from u/merfi on SO, added path param, exception.
    """
    head_dir = Path(path) / ".git" / "HEAD"
    with head_dir.open("r") as f:
        content = f.read().splitlines()
    for line in content:
        if line[0:4] == "ref:":
            return line.partition("refs/heads/")[2]
    raise GetBranchError()


def get_local_token():
    """Read the local file 'repo.txt' for a token, useful for testing."""
    try:
        with open("./repo.txt", "r") as repoF:
            return repoF.read(40)
    except FileNotFoundError:
        logging.info(
            "You can store your token at ./repo.txt and master-blaster will remember it while testing."
        )
        pass


def get_local_repo_url(configFile):
    for line in configFile:
        if line.find("url =") != -1:
            remoteOriginUrlStart = line.find("url =")
            return line[remoteOriginUrlStart + 6 : -1]


def get_local_repos(repos, localDirectory):
    repoNames = [repo["name"] for repo in repos]
    for root, subdirs, files in os.walk(f"{localDirectory}"):
        for subdir in subdirs:
            if any(subdir == repoName for repoName in repoNames):
                try:
                    with open(f"{root}/{subdir}/.git/config", "r") as configFile:
                        for repo in repos:
                            if subdir == repo["name"]:
                                repo["configUrl"] = get_local_repo_url(
                                    configFile
                                ).lower()
                                repo["localPath"] = f"{root}/{subdir}"
                                repo[
                                    "currentBranch"
                                ] = f"{get_current_branch(f'{root}/{subdir}')}"
                                repo["status"] = None
                                repoNames.remove(subdir)
                except Exception as err:
                    for repo in repos:
                        if subdir == repo["name"]:
                            repo[
                                "status"
                            ] = "Local folder that possibly isn't git repo, error opening .git/config"
                            repo["localPath"] = f"{root}/{subdir}"
                    continue
    for repo in repos:
        try:
            if (
                repo["status"]
                == "Local folder that possibly isn't git repo, error opening .git/config"
            ):
                logging.warning(
                    f"Error with {repo['name']}: Local folder(s) found without .git/config files, path unclear. Last checked directory: {repo['localPath']}"
                )
        except KeyError:
            pass
    return repos


def process_runner(string, process, *args):
    """Logs the argument to be attempted to run, runs it, logs and returns
    stdout and stderr."""
    logging.info(string)
    stdout, stderr = process.communicate()
    if len(stdout) > 0:
        logging.info(stdout)
    if len(stderr) > 0:
        if len(args) > 0:
            for ignoreString in args:
                if ignoreString in stderr.decode():
                    logging.warning(stderr)
                    logging.info("You may be able to ignore the above warning.")
                    return stdout, stderr
        logging.warning(stderr)
    return stdout, stderr


def set_current_branch(branch):
    """Set the current git branch, useful in testing to set it back to original."""
    setBranch = Popen(["git", "checkout", f"{branch}"], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process_runner(
        f"cwd={Path.cwd()}: git checkout {branch}", setBranch, "Already"
    )
    if len(stderr) > 0 and not "Already" in stderr:
        raise SetBranchError(stderr.decode())


def check_local_branches(repos):
    """Determine presence of target/master branches, and what the default is."""
    for repo in repos:
        if repo.get("localPath"):
            gitBranch = Popen(
                ["git", "branch"], cwd=repo["localPath"], stdout=PIPE, stderr=PIPE
            )
            stdout, stderr = process_runner(
                f"cwd={repo['localPath']}: git branch", gitBranch
            )
            if len(stderr) > 0:
                logging.warning("Fail in git branch!")
                raise
            repo["localHasMaster"] = "master" in f"{stdout}"
            repo["localHasTarget"] = repo["targetName"] in f"{stdout}"
            if not repo["hasTarget"] and not repo["hasMaster"]:
                repo["localHasThird"] = repo["default"] in f"{stdout}"
    return repos


def rename_branch(initial, final, directory):
    """Renames a branch of a repo, locally."""
    gitBranchMove = Popen(
        ["git", "branch", "-m", initial, final], cwd=directory, stdout=PIPE, stderr=PIPE
    )
    stdout, stderr = process_runner(
        f"cwd={directory}: git branch -m {initial} {final}", gitBranchMove
    )
    if len(stderr) > 0:
        raise RenameBranchError(directory, stderr.decode())


def push_setting_upstream(targetName, directory):
    """Pushes to remote, setting the remote tracking branch."""
    gitPushSetUpstream = Popen(
        ["git", "push", "-u", "origin", targetName],
        cwd={directory},
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = process_runner(
        f"cwd={directory}: git push -u origin {targetName}", gitPushSetUpstream
    )
    if len(stderr) > 0 and not "To" in stderr:
        raise PushBranchRenameError(directory, stderr.decode)


def delete_remote_branch(branch, directory):
    """Delete the old branch on the remote."""
    gitPushDelete = Popen(
        ["git", "push", "--delete", "origin", branch],
        cwd=directory,
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = process_runner(
        f"cwd={directory}: git push --delete origin {branch}", gitPushDelete
    )
    if len(stderr) > 0 and not "To" in stderr:
        raise DeleteRemoteError(branch, directory, stderr.decode())


def mkdir_if_need_be(username, localDirectory):
    """/master-blaster-{username} is used as a temp dir."""
    if not os.path.isdir(f"{localDirectory}/master-blaster-{username}/"):
        mkdir = Popen(
            ["mkdir", "-pv", f"{localDirectory}/master-blaster-{username}/"],
            cwd=localDirectory,
            stdout=PIPE,
            stderr=PIPE,
        )
        stdout, stderr = process_runner(
            f"cwd={localDirectory}: mkdir -pv {localDirectory}/master-blaster-{username}/",
            mkdir,
        )
        if len(stderr) > 0:
            raise MakeDirectoryError(localDirectory, stderr.decode())


def clone_repo(username, repo, localDirectory):
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
    stdout, stderr = process_runner(
        f"cwd={localDirectory}/master-blaster-{username}/: git clone {repo['htmlUrl']}.git ./{repo['owner-login']}/{repo['name']}",
        gitClone,
    )
    if len(stderr) > 0:
        raise CloneRepoError(stderr.decode())


def delete_local_branch(branch, directory):
    """Delete a local branch."""
    deleteBranch = Popen(
        ["git", "branch", "-D", branch], cwd={directory}, stdout=PIPE, stderr=PIPE
    )
    stdout, stderr = process_runner(
        f"cwd={directory}: git branch -D {branch}", deleteBranch
    )
    deleteBranchStderr = stdout, stderr[1]
    deleteBranchExitCode = stdout, stderr[2]
    if deleteBranchExitCode == 1:
        return deleteBranchStderr
    else:
        return None


def checkout(branch, directory):
    """Check out a branch."""
    checkoutBranch = Popen(
        ["git", "checkout", branch], cwd={directory}, stdout=PIPE, stderr=PIPE
    )
    stdout, stderr = process_runner(
        f"cwd={directory}: git checkout {branch}",
        checkoutBranch,
        ignoreStr="Already on",
        secondIgnoreStr="Switched to",
    )
    checkoutBranchStderr = process_runner[1]
    checkoutBranchExitCode = process_runner[2]
    if checkoutBranchExitCode == 1:
        return checkoutBranchStderr
    else:
        return None


def fetch(directory):
    gitFetch = Popen(["git", "fetch"], cwd={directory}, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process_runner(f"cwd={directory}: git fetch", gitFetch)
    gitFetchStderr = process_runner[1]
    gitFetchExitCode = process_runner[2]
    if gitFetchExitCode == 1:
        return gitFetchStderr
    else:
        return None


def unset_upstream(directory):
    gitBranchUU = Popen(
        ["git", "branch", "--unset-upstream"], cwd={directory}, stdout=PIPE, stderr=PIPE
    )
    stdout, stderr = process_runner(
        f"cwd={directory}: git branch --unset-upstream", gitBranchUU
    )
    gitBranchUUStderr = process_runner[1]
    gitBranchUUExitCode = process_runner[2]
    if gitBranchUUExitCode == 1:
        return gitBranchUUStderr
    else:
        return None


def set_upstream(targetName, directory):
    gitBranchSetUpstream = Popen(
        ["git", "branch", "-u", f"origin/{targetName}"],
        cwd={directory},
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = process_runner(
        f"cwd={directory}: git branch -u origin/{targetName}",
        gitBranchSetUpstream,
        ignoreStr="To",
    )
    gitBranchSetUpstreamStderr = process_runner[1]
    gitBranchSetUpstreamExitCode = process_runner[2]
    if gitBranchSetUpstreamExitCode == 1:
        return gitBranchSetUpstreamStderr
    else:
        return None


def update_symbolic_ref(targetName, directory):
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
    stdout, stderr = process_runner(
        f"cwd={directory}: git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/{targetName}",
        updateRef,
    )
    updateRefStderr = process_runner[1]
    updateRefExitCode = process_runner[2]
    if updateRefExitCode == 1:
        return updateRefStderr
    else:
        return None


def rm_clone_folder(username, localDirectory):
    removeDir = Popen(
        ["rm", "-dfRv", f"{localDirectory}/master-blaster-{username}/"],
        cwd={localDirectory},
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = process_runner(
        f"cwd={localDirectory}: rm -dfRv {localDirectory}/master-blaster-{username}/",
        removeDir,
    )
    removeDirStderr = process_runner[1]
    removeDirExitCode = process_runner[2]
    if removeDirExitCode == 1:
        return removeDirStderr
    else:
        return None


def git_new(targetName):
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
    stdout, stderr = process_runner(
        f"git config --global alias.new '!git init && git symbolic-ref HEAD refs/heads/{targetName}'",
        gitNew,
    )
    gitNewStderr = stdout, stderr[1]
    gitNewExitCode = stdout, stderr[2]
    if gitNewExitCode == 0:
        return gitNewStderr
    else:
        return None