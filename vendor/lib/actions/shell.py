import logging
import os
from pathlib import Path
from subprocess import Popen, PIPE
from vendor.lib.utils import states
from vendor.lib.actions.shell_exceptions import SetBranchError
from vendor.lib.actions.shell_exceptions import NoRemotesError
from vendor.lib.actions.shell_exceptions import NoUrlError
from vendor.lib.actions.shell_exceptions import MultipleRemotesError
from vendor.lib.actions.shell_exceptions import MultipleLocalReposError
from vendor.lib.actions.shell_exceptions import RenameBranchError
from vendor.lib.actions.shell_exceptions import PushBranchRenameError
from vendor.lib.actions.shell_exceptions import DeleteRemoteError
from vendor.lib.actions.shell_exceptions import MakeDirectoryError
from vendor.lib.actions.shell_exceptions import CloneRepoError
from vendor.lib.actions.shell_exceptions import DeleteLocalError
from vendor.lib.actions.shell_exceptions import CheckoutError
from vendor.lib.actions.shell_exceptions import FetchError
from vendor.lib.actions.shell_exceptions import UnsetUpstreamError
from vendor.lib.actions.shell_exceptions import SetUpstreamError
from vendor.lib.actions.shell_exceptions import UpdateRefError
from vendor.lib.actions.shell_exceptions import RemoveClonesError
from vendor.lib.actions.shell_exceptions import GitNewError


def get_current_branch(path):
    """Grab the current git branch.

    Credit:
        Mostly from u/merfi on SO, added path param, logging.
    """
    head_dir = Path(path) / ".git" / "HEAD"
    with head_dir.open("r") as f:
        content = f.read().splitlines()
    for line in content:
        if line[0:4] == "ref:":
            return line.partition("refs/heads/")[2]
    logging.warning(f"ERROR: Failed to get branch from {path}.")


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


def set_branch(branch, directory):
    """Set the git branch."""
    setBranch = Popen(
        ["git", "checkout", branch], cwd=directory, stdout=PIPE, stderr=PIPE
    )
    stdout, stderr = process_runner(
        f"cwd={directory}: git checkout {branch}", setBranch, "Already"
    )
    if len(stderr) > 0 and not "Already" in stderr.decode():
        raise SetBranchError(stderr.decode())


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


def check_for_remote_or_remotes_and_get_url(configFile):
    """Scan git config file for remote(s) and if there's one and
    a url, return it, otherwise return either error codes 0 for
    no remotes found, 1 for no url, and 2 for."""
    count = 0
    url = ""
    for line in configFile:
        if "[remote" in line:
            count += 1
        if "url =" in line:
            urlStart = line.find("url =")
            url = line[urlStart + 6 : -1]
    return url, count


def check_config(configFile, repos, testing):
    """Check a config file against the list of repos and return whether
    it's a match with any and how many remotes there are."""
    try:
        url, numRemotes = check_for_remote_or_remotes_and_get_url(configFile)
        # print(url)
        # print(numRemotes)
        if numRemotes == 0:
            raise NoRemotesError()
        if url == "":
            raise NoUrlError()
        for repo in repos:
            if testing:
                # git@github.com-monty_mcblaster1:
                # git@github.com:
                if url[31:] == repo["sshUrl"][14:]:
                    if numRemotes != 1:
                        raise MultipleRemotesError(repo)
                    return repo
            if url == repo["htmlUrl"] or url == repo["gitUrl"] or url == repo["sshUrl"]:
                if numRemotes != 1:
                    raise MultipleRemotesError(repo)
                return repo
        return None
    except (NoRemotesError, NoUrlError):
        pass


def fetch_dry_run(directory):
    """Checks if the local repo is in fact a repo and the url
    points to a remote that it shares a commit history with.

    Warning! I don't know that it errors after the *second* time!"""
    fetchDryRun = Popen(
        ["git", "fetch", "--dry-run", "--verbose"],
        cwd=directory,
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = process_runner(
        f"cwd={directory}: git fetch --dry-run --verbose", fetchDryRun, "From "
    )
    if len(stderr.decode()) > 0:
        if (
            "fatal: Could not read from remote" in stderr.decode()
            or "warning: no common commits" in stderr.decode()
        ):
            return False
        return True
    return False


def get_local_repos(repos, localDirectory, testing):
    """Walk the file system from the specified local directory and
    check for git config files, and return the repos with what we learn.
    Say, if it didn't find any, that maybe the git config file couldn't
    be read for some reason or that there was a multiple remotes or
    no url error."""
    for root, subdirs, files in os.walk(f"{localDirectory}"):
        for subdir in subdirs:
            try:
                with open(f"{root}/{subdir}/.git/config", "r") as configFile:
                    # print(f"{root}/{subdir}")
                    checkedRepo = check_config(configFile, repos, testing)
                    # print(checkedRepo)
                    if checkedRepo == None:
                        continue
                    for repo in repos:
                        if repo["name"] == checkedRepo["name"]:
                            remoteChecksOut = fetch_dry_run(f"{root}/{subdir}")
                            if repo.get("localPath"):
                                repo["status"].append(states["multipleLocals"])
                                raise MultipleLocalReposError(
                                    repo["name"], repo["localPath"], f"{root}/{subdir}/"
                                )
                            repo["localPath"] = f"{root}/{subdir}"
                            repo[
                                "currentBranch"
                            ] = f"{get_current_branch(f'{root}/{subdir}')}"
                            repo["status"] = []
            except FileNotFoundError:
                pass
            except MultipleRemotesError as err:
                logging.warning(err.message)
                for repo in repos:
                    if repo["name"] == err.repoName:
                        repo["status"].append(states["multipleRemotes"])
            except MultipleLocalReposError as err:
                logging.warning(err.message)
    # print("get_local_repos")
    # print(repos)
    return repos


def check_local_branches(repos):
    """Determine presence of target/master branches, and what the default is."""
    for repo in repos:
        if repo.get("localPath"):
            if (
                states["multipleLocals"] in repo["status"]
                or states["multipleRemotes"] in repo["status"]
                or states["rejectedResponse"] in repo["status"]
            ):
                continue
            gitBranch = Popen(
                ["git", "branch"], cwd=repo["localPath"], stdout=PIPE, stderr=PIPE
            )
            stdout, stderr = process_runner(
                f"cwd={repo['localPath']}: git branch", gitBranch
            )
            if len(stderr) > 0:
                logging.warning(f"Error in git branch! {repo['localPath']}")
                repo["status"].append(states["gitBranchError"])
                continue
            repo["localHasMaster"] = "master" in f"{stdout}"
            repo["localHasTarget"] = repo["targetName"] in f"{stdout}"
            if not repo["hasTarget"] and not repo["hasMaster"]:
                repo["localHasThird"] = repo["default"] in f"{stdout}"
    # print("check_local_branches")
    # print(repos)
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
        cwd=directory,
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = process_runner(
        f"cwd={directory}: git push -u origin {targetName}", gitPushSetUpstream, "To"
    )
    if len(stderr) > 0 and "fatal" in stderr.decode():
        raise PushBranchRenameError(directory, stderr.decode())


def delete_remote_branch(branch, directory):
    """Delete the old branch on the remote."""
    gitPushDelete = Popen(
        ["git", "push", "--delete", "origin", branch],
        cwd=directory,
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = process_runner(
        f"cwd={directory}: git push --delete origin {branch}", gitPushDelete, "To"
    )
    if len(stderr) > 0 and not "To" in stderr.decode():
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
            f"{repo['sshUrl']}",
            f"./{repo['ownerLogin']}/{repo['name']}",
        ],
        cwd=f"{localDirectory}/master-blaster-{username}/",
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = process_runner(
        f"cwd={localDirectory}/master-blaster-{username}/: git clone {repo['sshUrl']} ./{repo['ownerLogin']}/{repo['name']}",
        gitClone,
        "Cloning into",
    )
    if len(stderr) > 0 and "fatal" in stderr.decode():
        raise CloneRepoError(stderr.decode())


def delete_local_branch(branch, directory):
    """Delete a local branch."""
    deleteBranch = Popen(
        ["git", "branch", "-D", branch], cwd=directory, stdout=PIPE, stderr=PIPE
    )
    stdout, stderr = process_runner(
        f"cwd={directory}: git branch -D {branch}", deleteBranch
    )
    if len(stderr) > 0:
        raise DeleteLocalError(branch, directory, stderr.decode())


def checkout(branch, directory):
    """Check out a branch."""
    checkoutBranch = Popen(
        ["git", "checkout", branch], cwd=directory, stdout=PIPE, stderr=PIPE
    )
    stdout, stderr = process_runner(
        f"cwd={directory}: git checkout {branch}",
        checkoutBranch,
        "Already on",
        "Switched to",
    )
    if (
        len(stderr) > 0
        and not "Already on" in stderr.decode()
        and not "Switched to" in stderr.decode()
    ):
        raise CheckoutError(branch, directory, stderr.decode())


def fetch(directory):
    gitFetch = Popen(["git", "fetch"], cwd=directory, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process_runner(f"cwd={directory}: git fetch", gitFetch, "From ")
    if len(stderr) > 0 and "fatal" in stderr.decode():
        raise FetchError(directory, stderr.decode())


def unset_upstream(directory):
    gitBranchUU = Popen(
        ["git", "branch", "--unset-upstream"], cwd=directory, stdout=PIPE, stderr=PIPE
    )
    stdout, stderr = process_runner(
        f"cwd={directory}: git branch --unset-upstream", gitBranchUU
    )
    if len(stderr) > 0:
        raise UnsetUpstreamError(directory, stderr.decode())


def set_upstream(targetName, directory):
    gitBranchSetUpstream = Popen(
        ["git", "branch", "-u", f"origin/{targetName}"],
        cwd=directory,
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = process_runner(
        f"cwd={directory}: git branch -u origin/{targetName}",
        gitBranchSetUpstream,
        "To",
    )
    if len(stderr) > 0 and not "To" in stderr.decode():
        raise SetUpstreamError(directory, stderr.decode())


def update_symbolic_ref(targetName, directory):
    updateRef = Popen(
        [
            "git",
            "symbolic-ref",
            "refs/remotes/origin/HEAD",
            f"refs/remotes/origin/{targetName}",
        ],
        cwd=directory,
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = process_runner(
        f"cwd={directory}: git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/{targetName}",
        updateRef,
    )
    if len(stderr) > 0:
        raise UpdateRefError(directory, stderr.decode())


def rm_clone_folder(username, localDirectory):
    removeDir = Popen(
        ["rm", "-dfRv", f"{localDirectory}/master-blaster-{username}/"],
        cwd=localDirectory,
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = process_runner(
        f"cwd={localDirectory}: rm -dfRv {localDirectory}/master-blaster-{username}/",
        removeDir,
    )
    if len(stderr) > 0:
        raise RemoveClonesError(
            f"{localDirectory}/master-blaster-{username}/", stderr.decode()
        )


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
    if len(stderr) > 0:
        raise GitNewError(stderr.decode())
