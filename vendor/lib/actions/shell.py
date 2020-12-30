import logging
import os
from pathlib import Path
from subprocess import Popen, PIPE
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
    if count == 1 and url != "":
        return url
    if count == 0:
        raise NoRemotesError()
    if count == 1 and url == "":
        raise NoUrlError()
    if count > 1:
        raise MultipleRemotesError()


def check_config(configFile, repos):
    """Check a config file against the list of repos and return whether
    it's a match with any and how many remotes there are."""
    try:
        url = check_for_remote_or_remotes_and_get_url(configFile)
        for repo in repos:
            if url == repo["htmlUrl"] or url == repo["gitUrl"] or url == repo["sshUrl"]:
                return repo
        return None
    except NoRemotesError as err:
        logging.info(err.message)
    except NoUrlError as err:
        logging.info(err.message)
    except MultipleRemotesError as err:
        logging.info(err.message)


def get_local_repos(repos, localDirectory):
    """Walk the file system from the specified local directory and
    check for git config files, and return the repos with what we learn.
    Remember to say if it didn't find any that maybe the git config
    file couldn't be read for some reason or that there was a multiple
    remotes or no url error."""
    for root, subdirs, files in os.walk(f"{localDirectory}"):
        for subdir in subdirs:
            try:
                # FileNotFoundError
                with open(f"{root}/{subdir}/.git/config", "r") as configFile:
                    repo = check_config(configFile, repos)
                    if repo != None:
                        if repo.get("localPath"):
                            # repo["errors"].
                            raise MultipleLocalReposError(repo["name"], repo["localPath"], f"{root}/{subdir}/")



                        



def get_local_repos(repos, localDirectory):
    repoNames = [repo["name"] for repo in repos]
    for root, subdirs, files in os.walk(f"{localDirectory}"):
        for subdir in subdirs:
            # Here's where we lose it, because that the folder name
            # is the name of the repo is just a guess, and we're
            # not checking folders that aren't named the repo when they
            # could be cloned in with a differently named directory
            if any(subdir == repoName for repoName in repoNames):
                try:
                    # FileNotFoundError
                    with open(f"{root}/{subdir}/.git/config", "r") as configFile:
                        for repo in repos:
                            # So again, broken right here.
                            if subdir == repo["name"]:
                                if not config_url_indicates_match(
                                    configFile, repo["ownerLogin"], repo["name"]
                                ):
                                    continue
                                # This should probably be done before checking the config
                                # file for url, right?
                                if check_for_multiple_remotes(configFile):
                                    raise MultipleRemotesError()
                                repo["localPath"] = f"{root}/{subdir}"
                                repo[
                                    "currentBranch"
                                ] = f"{get_current_branch(f'{root}/{subdir}')}"
                                repo["status"] = None
                                repoNames.remove(subdir)
                except MultipleRemotesError as err:
                    logging.warning(err)
                    repo["status"] = "Multiple remotes found in git config file."
                    print(
                        f"Multiple remotes found in git config file for {repo['name']} so the program is not making any changes."
                    )
                    break
                except Exception as err:
                    for repo in repos:
                        if subdir == repo["name"]:
                            repo[
                                "status"
                            ] = "Local folder that possibly isn't git repo, error opening .git/config from local directory."
                            repo["localPath"] = f"{root}/{subdir}"
                    continue
    for repo in repos:
        try:
            if (
                repo["status"]
                == "Local folder that possibly isn't git repo, error opening .git/config from local directory."
            ):
                logging.warning(
                    f"Error with {repo['name']}: Local folder(s) found without .git/config files, path unclear. Last checked directory: {repo['localPath']}"
                )
        except KeyError:
            pass
    return repos


def check_local_branches(repos):
    """Determine presence of target/master branches, and what the default is."""
    for repo in repos:
        if repo.get("localPath"):
            try:
                if (
                    repo["status"]
                    == "Local folder that possibly isn't git repo, error opening .git/config from local directory."
                    or repo["status"] == "Multiple remotes found in git config file."
                ):
                    continue
            except KeyError:
                pass
            gitBranch = Popen(
                ["git", "branch"], cwd=repo["localPath"], stdout=PIPE, stderr=PIPE
            )
            stdout, stderr = process_runner(
                f"cwd={repo['localPath']}: git branch", gitBranch
            )
            if len(stderr) > 0:
                logging.warning(f"Error in git branch! {repo['localPath']}")
                repo[
                    "status"
                ] = "There was an error running git branch when checking the local repo, so action stopped on that repo."
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
        cwd=directory,
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = process_runner(
        f"cwd={directory}: git push -u origin {targetName}", gitPushSetUpstream, "To"
    )
    if len(stderr) > 0 and not "To" in stderr.decode():
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
            f"{repo['htmlUrl']}.git",
            f"./{repo['ownerLogin']}/{repo['name']}",
        ],
        cwd=f"{localDirectory}/master-blaster-{username}/",
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = process_runner(
        f"cwd={localDirectory}/master-blaster-{username}/: git clone {repo['htmlUrl']}.git ./{repo['ownerLogin']}/{repo['name']}",
        gitClone,
    )
    if len(stderr) > 0:
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
        and not "Already on" in stderr
        and not "Switched to" in stderr.decode()
    ):
        raise CheckoutError(directory, stderr.decode())


def fetch(directory):
    gitFetch = Popen(["git", "fetch"], cwd=directory, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process_runner(f"cwd={directory}: git fetch", gitFetch)
    if len(stderr) > 0:
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
        cwd={directory},
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
