import logging
from vendor.lib.utils import Error
from vendor.lib.actions.shell import rename_branch
from vendor.lib.actions.shell import push_setting_upstream
from vendor.lib.actions.network import update_default_branch
from vendor.lib.actions.shell import delete_remote_branch
from vendor.lib.actions.shell import mkdir_if_need_be
from vendor.lib.actions.shell import clone_repo
from vendor.lib.actions.shell import delete_local_branch
from vendor.lib.actions.shell import checkout
from vendor.lib.actions.shell import fetch
from vendor.lib.actions.shell import unset_upstream
from vendor.lib.actions.shell import set_upstream
from vendor.lib.actions.shell import update_symbolic_ref
from vendor.lib.actions.shell import rm_clone_folder
from vendor.lib.actions.shell import git_new
from vendor.lib.reporting import report_on
from vendor.lib.actions.shell import get_current_branch
from vendor.lib.actions.shell import set_branch
from vendor.lib.actions.shell_exceptions import RenameBranchError
from vendor.lib.actions.shell_exceptions import PushBranchRenameError
from vendor.lib.actions.shell_exceptions import UpdateDefaultError
from vendor.lib.actions.shell_exceptions import DeleteRemoteError
from vendor.lib.actions.shell_exceptions import MakeDirectoryError
from vendor.lib.actions.shell_exceptions import CloneRepoError
from vendor.lib.actions.shell_exceptions import DeleteLocalError
from vendor.lib.actions.shell_exceptions import CheckoutError
from vendor.lib.actions.shell_exceptions import FetchError
from vendor.lib.actions.shell_exceptions import SetBranchError
from vendor.lib.actions.shell_exceptions import UnsetUpstreamError
from vendor.lib.actions.shell_exceptions import SetUpstreamError
from vendor.lib.actions.shell_exceptions import UpdateRefError
from vendor.lib.actions.shell_exceptions import RemoveClonesError
from vendor.lib.actions.shell_exceptions import GitNewError


clonedRepos = []


class ProcessError(Error):
    """Raised when one of the series of processes breaks.

    Attributes:
        name -- what the repo is called
        errorMessage -- the stderr from the process
    """

    def __init__(self, series, name, errorMessage):
        self.message = f"ERROR: Error in {series} for {name}! {errorMessage}"


def mv_third_to_target_local(token, repo):
    """Rename 'third' to target and push upstream, rename default branch
    on GitHub, and delete remote 'third'."""
    process = "'rename third to target from local repo process'"
    try:
        rename_branch(repo["default"], repo["targetName"], repo["localPath"])
        push_setting_upstream(repo["targetName"], repo["localPath"])
        update_default_branch(token, repo)
        delete_remote_branch(repo["default"], repo["localPath"])
    except RenameBranchError as err:
        logging.warning(err)
        raise ProcessError(
            process,
            repo["name"],
            f"Got an error trying to rename branch locally! {err}",
        )
    except PushBranchRenameError as err:
        logging.warning(err)
        try:
            rename_branch(repo["targetName"], repo["default"], repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch, but got an error pushing the change to remote, so the program tried to rename the branch back, but then got an error renaming it! {err}",
            )
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, but got an error pushing the change to remote, so the program renamed the branch back. {err}",
        )
    except UpdateDefaultError as err:
        logging.warning(err)
        try:
            rename_branch(repo["targetName"], repo["default"], repo["localPath"])
            push_setting_upstream(repo["default"], repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch and pushed the change to remote, but got an error changing the default branch on GitHub, so the program tried to change the name back, but then got another error! {err}",
            )
        except PushBranchRenameError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch and pushed the change to remote, but got an error changing the default branch on GitHub, so the program changed the name back, but then got an error pushing it to the remote! {err}",
            )
    except DeleteRemoteError as err:
        logging.warning(err)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, pushed the change to remote, and changed the default branch on GitHub, but got an error deleting the {repo['default']} branch on the remote! {err}",
        )


def mv_third_to_target_clone(token, repo, localDirectory):
    """Clone branch, rename third and push target upstream, rename default branch on GitHub, delete remote third."""
    process = "'rename third to target with a cloned repo process'"
    try:
        mkdir_if_need_be(repo["ownerLogin"], localDirectory)
        clone_repo(repo["ownerLogin"], token, repo, localDirectory)
        clonedRepos.append(repo)
        newPath = (
            f"{localDirectory}/master-blaster-{repo['ownerLogin']}/{repo['name']}/"
        )
        rename_branch(repo["default"], repo["targetName"], newPath)
        push_setting_upstream(repo["targetName"], newPath)
        update_default_branch(token, repo)
        delete_remote_branch(repo["default"], newPath)
    except MakeDirectoryError as err:
        logging.warning(err)
        raise ProcessError(
            process,
            repo["name"],
            f"Unable to make directory to clone repo into! {err}",
        )
    except CloneRepoError as err:
        logging.warning(err)
        raise ProcessError(process, repo["name"], f"Unable to clone repo! {err}")
    except RenameBranchError as err:
        logging.warning(err)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully cloned repo, but got an error trying to rename branch locally! {err}",
        )
    except PushBranchRenameError as err:
        logging.warning(err)
        try:
            rename_branch(repo["targetName"], repo["default"], newPath)
        except RenameBranchError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully cloned repo and renamed local branch, but got an error pushing the change to remote, so the program tried to rename the branch back, but then got another error! {err}",
            )
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully cloned repo and renamed local branch, but got an error pushing the change to remote, so the program renamed the branch back. {err}",
        )
    except UpdateDefaultError as err:
        logging.warning(err)
        try:
            rename_branch(repo["targetName"], repo["default"], newPath)
            push_setting_upstream(repo["default"], newPath)
        except RenameBranchError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully cloned repo, renamed local branch, pushed change to remote, but got an error changing the default branch on GitHub, so the program tried to change the name back, but got another error! {err}",
            )
        except PushBranchRenameError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully cloned repo, renamed local branch, and pushed the change to remote, but got an error changing the default branch on GitHub, so the program changed the name back, but got an error pushing the change to the remote! {err}",
            )
    except DeleteRemoteError as err:
        logging.warning(err)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully cloned repo, renamed local branch, pushed the change to remote, and changed the default branch on GitHub, but got an error deleting the {repo['default']} branch on the remote! {err}",
        )


def mv_third_to_target_and_blast_local_master(token, repo, localDirectory):
    """Rename third and push target upstream, rename the default branch on
    GitHub, delete remote third, and delete local master."""
    process = "'rename third to target and blast local master process'"
    try:
        rename_branch(repo["default"], repo["targetName"], repo["localPath"])
        push_setting_upstream(repo["targetName"], repo["localPath"])
        update_default_branch(token, repo)
        delete_remote_branch(repo["default"], repo["localPath"])
        delete_local_branch("master", repo["localPath"])
    except RenameBranchError as err:
        logging.warning(err)
        raise ProcessError(
            process,
            repo["name"],
            f"Tried to rename local branch, but got an error! {err}",
        )
    except PushBranchRenameError as err:
        logging.warning(err)
        try:
            rename_branch(repo["targetName"], repo["default"], repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch, but got an error pushing the change to remote, so the program tried to rename the branch back, but got another error! {err}",
            )
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, but got an error pushing th change to remote, so the program renamed the branch back. {err}",
        )
    except UpdateDefaultError as err:
        logging.warning(err)
        try:
            rename_branch(repo["targetName"], repo["default"], repo["localPath"])
            push_setting_upstream(repo["default"], repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch and pushed the change to remote, but got an error changing the default branch on GitHub on GitHub, so the program tried to change the name back, but got an error! {err}",
            )
        except PushBranchRenameError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch and pushed the change to remote, but got an error changing the default branch on GitHub, so the program changed the name back locally, but got an error pushing the change to the remote! {err}",
            )
    except DeleteRemoteError as err:
        logging.warning(err)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, pushed the change to remote, and changed the default branch on GitHub, but got an error deleting the {repo['default']} branch on the remote! {err}",
        )
    except DeleteLocalError as err:
        logging.warning(err)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, pushed the change to remote, changed the default branch on GitHub, and deleted {repo['default']} remotely, but failed to delete local master branch! {err}",
        )


def delete_remote_process(token, repo, localDirectory):
    """Check if there's a local repo, then either clone or in-place push delete master."""
    if repo["localPath"]:
        try:
            delete_remote_branch("master", repo["localPath"])
        except DeleteRemoteError as err:
            logging.warning(err)
            raise ProcessError(
                "'blast remote master from local repo process'",
                repo["localPath"],
                f"Unable to blast remote master for {repo['name']}! {err}",
            )
    else:
        process = "'clone and blast remote master process'"
        try:
            mkdir_if_need_be(repo["ownerLogin"], localDirectory)
            clone_repo(repo["ownerLogin"], token, repo, localDirectory)
            clonedRepos.append(repo)
            newPath = (
                f"{localDirectory}/master-blaster-{repo['ownerLogin']}/{repo['name']}/"
            )
            delete_remote_branch(repo["default"], newPath)
        except MakeDirectoryError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Unable to make directory to clone repo into! {err}",
            )
        except CloneRepoError as err:
            logging.warning(err)
            raise ProcessError(process, repo["name"], f"Unable to clone repo! {err}")
        except DeleteRemoteError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully cloned repo, but got an error blasting master branch on the remote! {err}",
            )


def delete_local_and_remote(repo):
    """Delete remote and local master branches."""
    process = "'delete remote and local master branches process'"
    try:
        delete_remote_branch("master", repo["localPath"])
        delete_local_branch("master", repo["localPath"])
    except DeleteRemoteError as err:
        logging.warning(err)
        raise ProcessError(
            process, repo["name"], f"got an error blasting master on the remote! {err}"
        )
    except DeleteLocalError as err:
        logging.warning(err)
        raise ProcessError(
            process,
            repo["name"],
            f"Master blasted on the remote, but failed to blast master locally! {err}",
        )


def local_process(repo):
    """To sync up a local repo whose remote has been blasted, check out master,
    move it to target, fetch, unset the upstream, set the upstream, and update
    the symbolic ref."""
    process = (
        "'sync up local repo with remote repo which has already been blasted process'"
    )
    try:
        currentBranch = get_current_branch(repo["localPath"])
        checkout("master", repo["localPath"])
        rename_branch("master", repo["targetName"], repo["localPath"])
        fetch(repo["localPath"])
        unset_upstream(repo["localPath"])
        set_upstream(repo["targetName"], repo["localPath"])
        update_symbolic_ref(repo["targetName"], repo["localPath"])
    except CheckoutError as err:
        logging.warning(err)
        raise ProcessError(
            process,
            repo["name"],
            f"Failed to checkout master branch from {repo['localPath']}! {err}",
        )
    except RenameBranchError as err:
        logging.warning(err)
        if currentBranch != None:
            try:
                set_branch(currentBranch, repo["localPath"])
            except SetBranchError as err:
                logging.warning(err)
                pass
        raise ProcessError(
            process,
            repo["name"],
            f"Tried to rename local branch, but got an error! {err}",
        )
    except FetchError as err:
        logging.warning(err)
        try:
            rename_branch(repo["targetName"], "master", repo["localPath"])
            if currentBranch != None:
                set_branch(currentBranch, repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed branch, but got an error fetching refs from remote, so the program tried to name it back, but got another error! {err}",
            )
        except SetBranchError as err:
            logging.warning(err)
            pass
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed branch, but got an error fetching refs from remote, so the program renamed it back. {err}",
        )
    except UnsetUpstreamError as err:
        logging.warning(err)
        if currentBranch != None and currentBranch != "master":
            try:
                set_branch(currentBranch, repo["localPath"])
            except SetBranchError as err:
                logging.warning(err)
                pass
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed branch and fetched refs from remote, but got an error unsetting the upstream information! The program does NOT take any steps to recover at this point and leaves the following commands up to the user to run to continue the process! (From the project directory): `git branch --unset-upstream && git branch -u {repo['targetName']} && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/{repo['targetName']}` {err}",
        )
    except SetUpstreamError as err:
        logging.warning(err)
        if currentBranch != None and currentBranch != "master":
            try:
                set_branch(currentBranch, repo["localPath"])
            except SetBranchError as err:
                logging.warning(err)
                pass
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed branch and fetched refs from remote, and unset the upstream information, but got an error setting it again! The program does NOT take any steps to recover at this point and leaves the following commands up to the user to run to continue the process! (From the project directory): `git branch -u {repo['targetName']} && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/{repo['targetName']}` {err}",
        )
    except UpdateRefError as err:
        logging.warning(err)
        if currentBranch != None and currentBranch != "master":
            try:
                set_branch(currentBranch, repo["localPath"])
            except SetBranchError as err:
                logging.warning(err)
                pass
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed branch and fetched refs from remote, unset the upstream information, set it again, but got an error updating the symbolic ref! The program does NOT take any steps to recover at this point and leaves the following command up to the user to run to continue the process! (From the project directory): `git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/{repo['targetName']}` {err}",
        )


def remote_process_local(token, repo):
    """Move the branch, push that upstream, change the default branch on
    GitHub, and delete remote master branch."""
    process = "'blast master locally and on remote from local repo process'"
    try:
        rename_branch("master", repo["targetName"], repo["localPath"])
        push_setting_upstream(repo["targetName"], repo["localPath"])
        update_default_branch(token, repo)
        delete_remote_branch("master", repo["localPath"])
    except RenameBranchError as err:
        logging.warning(err)
        raise ProcessError(
            process,
            repo["name"],
            f"Tried to rename local branch, but got an error! {err}",
        )
    except PushBranchRenameError as err:
        logging.warning(err)
        try:
            rename_branch(repo["targetName"], "master", repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch, but got an error pushing the change to remote, so the program tried to rename the branch back, but got another error! {err}",
            )
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, but got an error pushing th change to remote, so the program renamed the branch back. {err}",
        )
    except UpdateDefaultError as err:
        logging.warning(err)
        try:
            rename_branch(repo["targetName"], "master", repo["localPath"])
            push_setting_upstream(repo["localPath"], "master")
        except RenameBranchError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch and pushed the change to remote, but got an error changing the default branch on GitHub on GitHub, so the program tried to change the name back, but got an error! {err}",
            )
        except PushBranchRenameError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch and pushed the change to remote, but got an error changing the default branch on GitHub, so the program changed the name back locally, but got an error pushing the change to the remote! {err}",
            )
    except DeleteRemoteError as err:
        logging.warning(err)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, pushed the change to remote, and changed the default branch on GitHub, but got an error deleting the master branch on the remote! {err}",
        )


def remote_process_clone(token, repo, localDirectory):
    """Mkdir if need be and clone the repo, then move the branch, push that
    upstream, change the default branch on GitHub, and delete remote master."""
    process = "'blast master on remote from cloned repo process'"
    try:
        mkdir_if_need_be(repo["ownerLogin"], localDirectory)
        clone_repo(repo["ownerLogin"], token, repo, localDirectory)
        clonedRepos.append(repo)
        newPath = (
            f"{localDirectory}/master-blaster-{repo['ownerLogin']}/{repo['name']}/"
        )
        rename_branch("master", repo["targetName"], newPath)
        push_setting_upstream(repo["targetName"], newPath)
        update_default_branch(token, repo)
        delete_remote_branch("master", newPath)
    except MakeDirectoryError as err:
        logging.warning(err)
        raise ProcessError(
            process,
            repo["name"],
            f"Unable to make directory to clone repo into! {err}",
        )
    except CloneRepoError as err:
        logging.warning(err)
        raise ProcessError(process, repo["name"], f"Unable to clone repo! {err}")
    except RenameBranchError as err:
        logging.warning(err)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully cloned repo, but got an error trying to rename local branch! {err}",
        )
    except PushBranchRenameError as err:
        logging.warning(err)
        try:
            rename_branch(repo["targetName"], "master", repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully cloned repo and renamed local branch, but got an error pushing the change to remote, so the program tried to rename the branch back, but then got another error! {err}",
            )
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully cloned repo and renamed local branch, but got an error pushing the change to remote, so the program renamed the branch back. {err}",
        )
    except UpdateDefaultError as err:
        logging.warning(err)
        try:
            rename_branch(repo["targetName"], "master", repo["localPath"])
            push_setting_upstream(repo["localPath"], "master")
        except RenameBranchError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully cloned repo, renamed local branch, and pushed the change to remote, but got an error changing the default branch on GitHub on GitHub, so the program tried to change the name back, but got an error! {err}",
            )
        except PushBranchRenameError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully cloned repo, renamed local branch, and pushed the change to remote, but got an error changing the default branch on GitHub, so the program changed the name back locally, but got an error pushing the change to the remote! {err}",
            )
    except DeleteRemoteError as err:
        logging.warning(err)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully cloned repo, renamed local branch, pushed the change to remote, and changed the default branch on GitHub, but got an error deleting the master branch on the remote!  {err}",
        )


def run(dataWithOptions):
    """Run any actions to be run, and report and log!"""
    (
        username,
        token,
        repos,
        optionRepos,
        localDirectory,
        removeClones,
        gitNew,
    ) = dataWithOptions
    states = {
        "pendingMvThirdToTargetLocal": "Do you want to mv third to target? Local repo",
        "mvThirdToTargetLocal": "Move third to target, local repo.",
        "pendingMvThirdToTargetClone": "Do you want to mv third to target? Clone repo",
        "mvThirdToTargetClone": "Move third to target, clone repo.",
        "pendingMvThirdToTargetAndBlastLocalMaster": "Do you want to mv third to target and blast the local master? Local repo.",
        "mvThirdToTargetAndBlastLocalMaster": "Move third to target and blast the local master, local repo.",
        "pendingDeleteRemote": "Delete remote?",
        "deleteRemote": "Delete remote.",
        "pendingDeleteLocal": "Delete local?",
        "deleteLocal": "Delete local.",
        "pendingDeleteLocalAndRemote": "Delete local and remote?",
        "deleteLocalAndRemote": "Delete local and remote.",
        "remoteProcessLocal": "Perfect remote process local repo.",
        "remoteProcessClone": "Perfect remote process clone repo.",
        "pendingLocalProcess": "Perfect case local process.",
        "localProcess": "Local process is a go.",
        "alreadyBlasted": "Already blasted.",
        "pathUnclear": "Path unclear.",
        "folderError": "Local folder that possibly isn't git repo, error opening .git/config",
    }

    # * optionRepos = {
    # *    "reposMvThirdToTargetLocal": reposMvThirdToTargetLocal,
    # *    "reposMvThirdToTargetClone": reposMvThirdToTargetClone,
    # *    "reposMvThirdToTargetAndBlastLocalMaster": reposMvThirdToTargetAndBlastLocalMaster,
    # *    "reposDeleteRemote": reposDeleteRemote,
    # *    "reposDeleteLocal": reposDeleteLocal,
    # *    "reposDeleteLocalAndRemote": reposDeleteLocalAndRemote,
    # *    "reposLocalProcess": reposLocalProcess,
    # *}

    reposRemoteProcessLocal = {"repos": [], "errors": []}
    reposRemoteProcessClone = {"repos": [], "errors": []}
    reposAlreadyBlasted = {"repos": []}
    reposPathUnclear = {"repos": []}
    reposFolderError = {"repos": []}

    for optionRepo in optionRepos:
        optionRepo["errors"] = []

    for repo in repos:
        if repo["status"] == states["remoteProcessLocal"]:
            reposRemoteProcessLocal["repos"].append(repo)
        if repo["status"] == states["remoteProcessClone"]:
            reposRemoteProcessClone["repos"].append(repo)
        if repo["status"] == states["alreadyBlasted"]:
            reposAlreadyBlasted["repos"].append(repo)
        if repo["status"] == states["pathUnclear"]:
            reposPathUnclear["repos"].append(repo)
        if repo["status"] == states["folderError"]:
            reposFolderError["repos"].append(repo)

    if len(optionRepos["reposMvThirdToTargetLocal"]["repos"]) > 0:
        for repo in optionRepos["reposMvThirdToTargetLocal"]["repos"]:
            try:
                mv_third_to_target_local(token, repo)
            except ProcessError as err:
                optionRepos["reposMvThirdToTargetLocal"]["errors"].append(
                    [repo, err.message]
                )

    if len(optionRepos["reposMvThirdToTargetClone"]["repos"]) > 0:
        for repo in optionRepos["reposMvThirdToTargetClone"]["repos"]:
            try:
                mv_third_to_target_clone(token, repo, localDirectory)
            except ProcessError as err:
                optionRepos["reposMvThirdToTargetClone"]["errors"].append(
                    [repo, err.message]
                )

    if len(optionRepos["reposMvThirdToTargetAndBlastLocalMaster"]["repos"]) > 0:
        for repo in optionRepos["reposMvThirdToTargetAndBlastLocalMaster"]["repos"]:
            try:
                mv_third_to_target_and_blast_local_master(repo)
            except ProcessError as err:
                optionRepos["reposMvThirdToTargetAndBlastLocalMaster"][
                    "errors"
                ].appendd([repo, err.message])

    if len(optionRepos["reposDeleteRemote"]["repos"]) > 0:
        for repo in optionRepos["reposDeleteRemote"]["repos"]:
            try:
                delete_remote_process("master", repo["localPath"])
            except ProcessError as err:
                optionRepos["reposDeleteRemote"]["errors"].append([repo, err.message])

    if len(optionRepos["reposDeleteLocal"]["repos"]) > 0:
        for repo in optionRepos["reposDeleteLocal"]["repos"]:
            try:
                delete_local_branch("master", repo["localPath"])
            except ProcessError as err:
                optionRepos["reposDeleteLocal"]["errors"].append([repo, err.message])

    if len(optionRepos["reposDeleteLocalAndRemote"]["repos"]) > 0:
        for repo in optionRepos["reposDeleteLocalAndRemote"]["repos"]:
            try:
                delete_local_and_remote(repo)
            except ProcessError as err:
                optionRepos["reposDeleteLocalAndRemote"]["errors"].append(
                    [repo, err.message]
                )

    if len(optionRepos["reposLocalProcess"]["repos"]) > 0:
        for repo in optionRepos["reposLocalProcess"]["repos"]:
            try:
                local_process(repo)
            except ProcessError as err:
                optionRepos["reposLocalProcess"]["errors"].append([repo, err.message])

    if len(reposRemoteProcessLocal["repos"]) > 0:
        for repo in reposRemoteProcessLocal["repos"]:
            try:
                remote_process_local(token, repo)
            except ProcessError as err:
                reposRemoteProcessLocal["errors"].append([repo, err.message])

    if len(reposRemoteProcessClone["repos"]) > 0:
        for repo in reposRemoteProcessClone["repos"]:
            try:
                remote_process_clone(token, repo, localDirectory)
            except ProcessError as err:
                reposRemoteProcessClone["errors"].append([repo, err.message])

    clonesRmAttempted = False
    reposCloneDeletionError = ""
    if removeClones and len(clonedRepos) > 0:
        clonesRmAttempted = True
        try:
            rm_clone_folder(username, localDirectory)
        except RemoveClonesError as err:
            reposCloneDeletionError = err.message

    gitNewError = False
    if gitNew:
        try:
            git_new(repo[0]["targetName"])
        except GitNewError as err:
            logging.warning(err)
            gitNewError = True
            print(
                f"Error adding the git alias `git new` failed! You can run `git config --global alias.new '!git init && git symbolic-ref HEAD refs/heads/{repos[0]['targetname']}` to try again!"
            )
            pass

    finalRepos = {
        "reposMvThirdToTargetLocal": optionRepos["reposMvThirdToTargetLocal"],
        "reposMvThirdToTargetClone": optionRepos["reposMvThirdToTargetClone"],
        "reposMvThirdToTargetAndBlastLocalMaster": optionRepos[
            "reposMvThirdToTargetAndBlastLocalMaster"
        ],
        "reposDeleteRemote": optionRepos["reposDeleteRemote"],
        "reposDeleteLocal": optionRepos["reposDeleteLocal"],
        "reposDeleteLocalAndRemote": optionRepos["reposDeleteLocalAndRemote"],
        "reposLocalProcess": optionRepos["reposLocalProcess"],
        "reposRemoteProcessLocal": reposRemoteProcessLocal,
        "reposRemoteProcessClone": reposRemoteProcessClone,
        "reposAlreadyBlasted": reposAlreadyBlasted,
        "reposPathUnclear": reposPathUnclear,
        "reposFolderError": reposFolderError,
    }

    report_on(
        finalRepos, clonesRmAttempted, reposCloneDeletionError, gitNew, gitNewError
    )
