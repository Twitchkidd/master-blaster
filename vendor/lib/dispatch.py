import logging
from vendor.lib.utils import Error
from vendor.lib.actions.shell import check_for_remote_or_remotes_and_get_url
from vendor.lib.utils import states
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
from vendor.lib.actions.shell_exceptions import MultipleRemotesError
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


def mv_third_to_target_local_repo(token, repo):
    """Rename 'third' to target and push upstream, rename default branch
    on GitHub, and delete remote 'third'."""
    process = "'rename third to target from local repo process'"
    try:
        rename_branch(repo["default"], repo["targetName"], repo["localPath"])
        push_setting_upstream(repo["targetName"], repo["localPath"])
        update_default_branch(token, repo)
        delete_remote_branch(repo["default"], repo["localPath"])
    except RenameBranchError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Got an error trying to rename branch locally! {err.message}",
        )
    except PushBranchRenameError as err:
        logging.warning(err.message)
        try:
            rename_branch(repo["targetName"], repo["default"], repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch, but got an error pushing the change to remote, so the program tried to rename the branch back, but then got an error renaming it! {err.message}",
            )
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, but got an error pushing the change to remote, so the program renamed the branch back. {err.message}",
        )
    except UpdateDefaultError as err:
        logging.warning(err.message)
        try:
            rename_branch(repo["targetName"], repo["default"], repo["localPath"])
            push_setting_upstream(repo["default"], repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch and pushed the change to remote, but got an error changing the default branch on GitHub, so the program tried to change the name back, but then got another error! {err.message}",
            )
        except PushBranchRenameError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch and pushed the change to remote, but got an error changing the default branch on GitHub, so the program changed the name back, but then got an error pushing it to the remote! {err.message}",
            )
    except DeleteRemoteError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, pushed the change to remote, and changed the default branch on GitHub, but got an error deleting the {repo['default']} branch on the remote! {err.message}",
        )


def mv_third_to_target_clone_repo(token, repo, localDirectory):
    """Clone repo, rename third and push target upstream, rename default branch on GitHub, delete remote third."""
    process = "'rename third to target with a cloned repo process'"
    try:
        mkdir_if_need_be(repo["ownerLogin"], localDirectory)
        clone_repo(repo["ownerLogin"], repo, localDirectory)
        clonedRepos.append(repo)
        newPath = f"{localDirectory}/master-blaster-{repo['ownerLogin']}/{repo['ownerLogin']}/{repo['name']}/"
        with open(f"{newPath}.git/config", "r") as configFile:
            if check_for_remote_or_remotes_and_get_url(configFile)[1] > 1:
                raise MultipleRemotesError()
        rename_branch(repo["default"], repo["targetName"], newPath)
        push_setting_upstream(repo["targetName"], newPath)
        update_default_branch(token, repo)
        delete_remote_branch(repo["default"], newPath)
    except MakeDirectoryError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Unable to make directory to clone repo into! {err.message}",
        )
    except CloneRepoError as err:
        logging.warning(err.message)
        raise ProcessError(
            process, repo["name"], f"Unable to clone repo! {err.message}"
        )
    except MultipleRemotesError as err:
        logging.warning(err.message)
        repo["status"] = "Multiple remotes found in git config file."
        raise ProcessError(process, repo["name"], err.message)
    except RenameBranchError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully cloned repo, but got an error trying to rename branch locally! {err.message}",
        )
    except PushBranchRenameError as err:
        logging.warning(err.message)
        try:
            rename_branch(repo["targetName"], repo["default"], newPath)
        except RenameBranchError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully cloned repo and renamed local branch, but got an error pushing the change to remote, so the program tried to rename the branch back, but then got another error! {err.message}",
            )
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully cloned repo and renamed local branch, but got an error pushing the change to remote, so the program renamed the branch back. {err.message}",
        )
    except UpdateDefaultError as err:
        logging.warning(err.message)
        try:
            rename_branch(repo["targetName"], repo["default"], newPath)
            push_setting_upstream(repo["default"], newPath)
        except RenameBranchError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully cloned repo, renamed local branch, pushed change to remote, but got an error changing the default branch on GitHub, so the program tried to change the name back, but got another error! {err.message}",
            )
        except PushBranchRenameError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully cloned repo, renamed local branch, and pushed the change to remote, but got an error changing the default branch on GitHub, so the program changed the name back, but got an error pushing the change to the remote! {err.message}",
            )
    except DeleteRemoteError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully cloned repo, renamed local branch, pushed the change to remote, and changed the default branch on GitHub, but got an error deleting the {repo['default']} branch on the remote! {err.message}",
        )


def mv_third_to_target_and_delete_remote_master_local_repo(token, repo):
    """Rename third and push target upstream, rename the default branch on
    GitHub, delete remote third, and delete remote master from a local repo."""
    process = "'rename third to target and blast remote master from local repo process'"
    try:
        rename_branch(repo["default"], repo["targetName"], repo["localPath"])
        push_setting_upstream(repo["targetName"], repo["localPath"])
        update_default_branch(token, repo)
        delete_remote_branch(repo["default"], repo["localPath"])
        delete_remote_branch("master", repo["localPath"])
    except RenameBranchError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Tried to rename local branch, but got an error! {err.message}",
        )
    except PushBranchRenameError as err:
        logging.warning(err.message)
        try:
            rename_branch(repo["targetName"], repo["default"], repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch, but got an error pushing the change to remote, so the program tried to rename the branch back, but got another error! {err.message}",
            )
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, but got an error pushing th change to remote, so the program renamed the branch back. {err.message}",
        )
    except UpdateDefaultError as err:
        logging.warning(err.message)
        try:
            rename_branch(repo["targetName"], repo["default"], repo["localPath"])
            push_setting_upstream(repo["default"], repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch and pushed the change to remote, but got an error changing the default branch on GitHub on GitHub, so the program tried to change the name back, but got an error! {err.message}",
            )
        except PushBranchRenameError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch and pushed the change to remote, but got an error changing the default branch on GitHub, so the program changed the name back locally, but got an error pushing the change to the remote! {err.message}",
            )
    except DeleteRemoteError as err:
        logging.warning(err.message)
        if err.branch == repo["default"]:
            try:
                delete_remote_branch("master", repo["localPath"])
            except DeleteRemoteError as err:
                logging.warning(err.message)
                raise ProcessError(
                    process,
                    repo["name"],
                    f"Successfully renamed local branch, pushed the change to remote, and changed the default branch on GitHub, got an error deleting the {repo['default']} branch on the remote, and then got another error deleting the master branch on the remote! {err.message}",
                )
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch, pushed the change to remote, changed the default branch on GitHub, and deleted the master branch on the remote, but got an error deleting the {repo['default']} branch on the remote! {err.message}",
            )
        else:
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch, pushed the change to remote, changed the default branch on GitHub, and deleted the {repo['default']} branch on the remote, but got an error deleting the master branch on the remote! {err.message}",
            )


def mv_third_to_target_and_delete_remote_master_clone_repo(token, repo, localDirectory):
    """Clone repo, rename third and push target upstream, rename the default branch on
    GitHub, delete remote third, and delete remote master from a cloned repo."""
    process = (
        "'rename third to target and blast remote master from cloned repo process'"
    )
    try:
        mkdir_if_need_be(repo["ownerLogin"], localDirectory)
        clone_repo(repo["ownerLogin"], repo, localDirectory)
        clonedRepos.append(repo)
        newPath = f"{localDirectory}/master-blaster-{repo['ownerLogin']}/{repo['ownerLogin']}/{repo['name']}/"
        with open(f"{newPath}.git/config", "r") as configFile:
            if check_for_remote_or_remotes_and_get_url(configFile)[1] > 1:
                raise MultipleRemotesError()
        rename_branch(repo["default"], repo["targetName"], repo["localPath"])
        push_setting_upstream(repo["targetName"], repo["localPath"])
        update_default_branch(token, repo)
        delete_remote_branch(repo["default"], repo["localPath"])
        delete_remote_branch("master", repo["localPath"])
    except MakeDirectoryError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Unable to make directory to clone repo into! {err.message}",
        )
    except CloneRepoError as err:
        logging.warning(err.message)
        raise ProcessError(
            process, repo["name"], f"Unable to clone repo! {err.message}"
        )
    except MultipleRemotesError as err:
        logging.warning(err.message)
        repo["status"] = "Multiple remotes found in git config file."
        raise ProcessError(process, repo["name"], err.message)
    except RenameBranchError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Tried to rename local branch, but got an error! {err.message}",
        )
    except PushBranchRenameError as err:
        logging.warning(err.message)
        try:
            rename_branch(repo["targetName"], repo["default"], repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch, but got an error pushing the change to remote, so the program tried to rename the branch back, but got another error! {err.message}",
            )
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, but got an error pushing th change to remote, so the program renamed the branch back. {err.message}",
        )
    except UpdateDefaultError as err:
        logging.warning(err.message)
        try:
            rename_branch(repo["targetName"], repo["default"], repo["localPath"])
            push_setting_upstream(repo["default"], repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch and pushed the change to remote, but got an error changing the default branch on GitHub on GitHub, so the program tried to change the name back, but got an error! {err.message}",
            )
        except PushBranchRenameError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch and pushed the change to remote, but got an error changing the default branch on GitHub, so the program changed the name back locally, but got an error pushing the change to the remote! {err.message}",
            )
    except DeleteRemoteError as err:
        logging.warning(err.message)
        if err.branch == repo["default"]:
            try:
                delete_remote_branch("master", repo["localPath"])
            except DeleteRemoteError as err:
                logging.warning(err.message)
                raise ProcessError(
                    process,
                    repo["name"],
                    f"Successfully renamed local branch, pushed the change to remote, and changed the default branch on GitHub, got an error deleting the {repo['default']} branch on the remote, and then got another error deleting the master branch on the remote! {err.message}",
                )
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch, pushed the change to remote, changed the default branch on GitHub, and deleted the master branch on the remote, but got an error deleting the {repo['default']} branch on the remote! {err.message}",
            )
        else:
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch, pushed the change to remote, changed the default branch on GitHub, and deleted the {repo['default']} branch on the remote, but got an error deleting the master branch on the remote! {err.message}",
            )


def mv_third_to_target_and_delete_remote_and_local_master(token, repo):
    """Rename third and push target upstream, rename the default branch on
    GitHub, delete remote third, and delete remote and local master branches."""
    process = "'rename third to target and blast remote and local masters process'"
    try:
        rename_branch(repo["default"], repo["targetName"], repo["localPath"])
        push_setting_upstream(repo["targetName"], repo["localPath"])
        update_default_branch(token, repo)
        delete_remote_branch(repo["default"], repo["localPath"])
        delete_remote_branch("master", repo["localPath"])
        checkout(repo["targetName"], repo["localPath"])
        delete_local_branch("master", repo["localPath"])
    except RenameBranchError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Tried to rename local branch, but got an error! {err.message}",
        )
    except PushBranchRenameError as err:
        logging.warning(err.message)
        try:
            rename_branch(repo["targetName"], repo["default"], repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch, but got an error pushing the change to remote, so the program tried to rename the branch back, but got another error! {err.message}",
            )
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, but got an error pushing th change to remote, so the program renamed the branch back. {err.message}",
        )
    except UpdateDefaultError as err:
        logging.warning(err.message)
        try:
            rename_branch(repo["targetName"], repo["default"], repo["localPath"])
            push_setting_upstream(repo["default"], repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch and pushed the change to remote, but got an error changing the default branch on GitHub on GitHub, so the program tried to change the name back, but got an error! {err.message}",
            )
        except PushBranchRenameError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch and pushed the change to remote, but got an error changing the default branch on GitHub, so the program changed the name back locally, but got an error pushing the change to the remote! {err.message}",
            )
    except DeleteRemoteError as err:
        logging.warning(err.message)
        if err.branch == repo["default"]:
            try:
                delete_remote_branch("master", repo["localPath"])
            except DeleteRemoteError as err:
                logging.warning(err.message)
                raise ProcessError(
                    process,
                    repo["name"],
                    f"Successfully renamed local branch, pushed the change to remote, and changed the default branch on GitHub, got an error deleting the {repo['default']} branch on the remote, and then got another error deleting the master branch on the remote! {err.message}",
                )
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch, pushed the change to remote, changed the default branch on GitHub, and deleted the master branch on the remote, but got an error deleting the {repo['default']} branch on the remote! {err.message}",
            )
        else:
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch, pushed the change to remote, changed the default branch on GitHub, and deleted the {repo['default']} branch on the remote, but got an error deleting the master branch on the remote! {err.message}",
            )
    except CheckoutError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, pushed the change to remote, changed the default branch on GitHub, deleted the {repo['default']} branch on the remote, deleted the master branch on the remote, but got an error running git checkout trying to delete the local master branch! {err.message}",
        )
    except DeleteLocalError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, pushed the change to remote, changed the default branch on GitHub, deleted the {repo['default']} branch on the remote, and deleted the master branch on the remote, but got an error deleting the master branch in the local repo! {err.message}",
        )


def mv_third_to_target_and_delete_local_master(token, repo):
    """Rename third and push target upstream, rename the default branch on
    GitHub, delete remote third, and delete local master."""
    process = "'rename third to target and blast local master process'"
    try:
        rename_branch(repo["default"], repo["targetName"], repo["localPath"])
        push_setting_upstream(repo["targetName"], repo["localPath"])
        update_default_branch(token, repo)
        delete_remote_branch(repo["default"], repo["localPath"])
        checkout(repo["targetName"], repo["localPath"])
        delete_local_branch("master", repo["localPath"])
    except RenameBranchError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Tried to rename local branch, but got an error! {err.message}",
        )
    except PushBranchRenameError as err:
        logging.warning(err.message)
        try:
            rename_branch(repo["targetName"], repo["default"], repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch, but got an error pushing the change to remote, so the program tried to rename the branch back, but got another error! {err.message}",
            )
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, but got an error pushing th change to remote, so the program renamed the branch back. {err.message}",
        )
    except UpdateDefaultError as err:
        logging.warning(err.message)
        try:
            rename_branch(repo["targetName"], repo["default"], repo["localPath"])
            push_setting_upstream(repo["default"], repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch and pushed the change to remote, but got an error changing the default branch on GitHub on GitHub, so the program tried to change the name back, but got an error! {err.message}",
            )
        except PushBranchRenameError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch and pushed the change to remote, but got an error changing the default branch on GitHub, so the program changed the name back locally, but got an error pushing the change to the remote! {err.message}",
            )
    except DeleteRemoteError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, pushed the change to remote, and changed the default branch on GitHub, but got an error deleting the {repo['default']} branch on the remote! {err.message}",
        )
    except CheckoutError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, pushed the change to remote, changed the default branch on GitHub, deleted the {repo['default']} branch on the remote, and deleted the master branch on the remote, but got an error running git checkout trying to delete the local master branch! {err.message}",
        )
    except DeleteLocalError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, pushed the change to remote, changed the default branch on GitHub, and deleted {repo['default']} remotely, but failed to delete local master branch! {err.message}",
        )


def delete_remote_master_local_repo(repo):
    """Delete a stray master branch on the remote from a local repo."""
    process = "'delete remote master from local repo process'"
    try:
        delete_remote_branch("master", repo["localPath"])
    except DeleteRemoteError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["localPath"],
            f"Unable to blast remote master! {err.message}",
        )


def delete_remote_master_clone_repo(token, repo, localDirectory):
    """Delete a stray master branch on the remote from a cloned repo."""
    process = "'clone and blast remote master process'"
    try:
        mkdir_if_need_be(repo["ownerLogin"], localDirectory)
        clone_repo(repo["ownerLogin"], repo, localDirectory)
        clonedRepos.append(repo)
        newPath = f"{localDirectory}/master-blaster-{repo['ownerLogin']}/{repo['ownerLogin']}/{repo['name']}/"
        with open(f"{newPath}.git/config", "r") as configFile:
            if check_for_remote_or_remotes_and_get_url(configFile)[1] > 1:
                raise MultipleRemotesError()
        delete_remote_branch("master", newPath)
    except MakeDirectoryError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Unable to make directory to clone repo into! {err.message}",
        )
    except CloneRepoError as err:
        logging.warning(err.message)
        raise ProcessError(
            process, repo["name"], f"Unable to clone repo! {err.message}"
        )
    except MultipleRemotesError as err:
        logging.warning(err.message)
        repo["status"] = "Multiple remotes found in git config file."
        raise ProcessError(process, repo["name"], err.message)
    except DeleteRemoteError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully cloned repo, but got an error blasting master branch on the remote! {err.message}",
        )


def delete_remote_and_local_master(repo):
    """Delete remote and local master branches."""
    process = "'delete remote and local master branches process'"
    try:
        delete_remote_branch("master", repo["localPath"])
        checkout(repo["targetName"], repo["localPath"])
        delete_local_branch("master", repo["localPath"])
    except DeleteRemoteError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Got an error blasting master on the remote! {err.message}",
        )
    except CheckoutError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully deleted the master branch on the remote, but got an error running git checkout trying to delete the local master branch! {err.message}",
        )
    except DeleteLocalError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Master blasted on the remote, but failed to blast master locally! {err.message}",
        )


def delete_local_master(repo):
    """Delete local master branch."""
    process = "'delete local master process'"
    try:
        checkout(repo["targetName"], repo["localPath"])
        delete_local_branch("master", repo["localPath"])
    except CheckoutError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Got an error running git checkout trying to delete the local master branch! {err.message}",
        )
    except DeleteLocalError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Got an error deleting local master branch! {err.message}",
        )


def local_update_process(repo):
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
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Failed to checkout master branch! {err.message}",
        )
    except RenameBranchError as err:
        logging.warning(err.message)
        if currentBranch != None:
            try:
                set_branch(currentBranch, repo["localPath"])
            except SetBranchError as err:
                logging.warning(err.message)
                pass
        raise ProcessError(
            process,
            repo["name"],
            f"Tried to rename local branch, but got an error! {err.message}",
        )
    except FetchError as err:
        logging.warning(err.message)
        try:
            rename_branch(repo["targetName"], "master", repo["localPath"])
            if currentBranch != None:
                set_branch(currentBranch, repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed branch, but got an error fetching refs from remote, so the program tried to name it back, but got another error! {err.message}",
            )
        except SetBranchError as err:
            logging.warning(err.message)
            pass
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed branch, but got an error fetching refs from remote, so the program renamed it back. {err.message}",
        )
    except UnsetUpstreamError as err:
        logging.warning(err.message)
        if currentBranch != None and currentBranch != "master":
            try:
                set_branch(currentBranch, repo["localPath"])
            except SetBranchError as err:
                logging.warning(err.message)
                pass
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed branch and fetched refs from remote, but got an error unsetting the upstream information! The program does NOT take any steps to recover at this point and leaves the following commands up to the user to run to continue the process! (From the project directory): `git branch --unset-upstream && git branch -u {repo['targetName']} && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/{repo['targetName']}`",
        )
    except SetUpstreamError as err:
        logging.warning(err.message)
        if currentBranch != None and currentBranch != "master":
            try:
                set_branch(currentBranch, repo["localPath"])
            except SetBranchError as err:
                logging.warning(err.message)
                pass
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed branch and fetched refs from remote, and unset the upstream information, but got an error setting it again! The program does NOT take any steps to recover at this point and leaves the following commands up to the user to run to continue the process! (From the project directory): `git branch -u {repo['targetName']} && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/{repo['targetName']}` {err.message}",
        )
    except UpdateRefError as err:
        logging.warning(err.message)
        if currentBranch != None and currentBranch != "master":
            try:
                set_branch(currentBranch, repo["localPath"])
            except SetBranchError as err:
                logging.warning(err.message)
                pass
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed branch and fetched refs from remote, unset the upstream information, set it again, but got an error updating the symbolic ref! The program does NOT take any steps to recover at this point and leaves the following command up to the user to run to continue the process! (From the project directory): `git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/{repo['targetName']}` {err.message}",
        )


def remote_process_local_repo(token, repo):
    """Move the branch, push that upstream, change the default branch on
    GitHub, and delete remote master branch."""
    process = "'blast master locally and on remote from local repo process'"
    try:
        rename_branch("master", repo["targetName"], repo["localPath"])
        push_setting_upstream(repo["targetName"], repo["localPath"])
        update_default_branch(token, repo)
        delete_remote_branch("master", repo["localPath"])
    except RenameBranchError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Tried to rename local branch, but got an error! {err.message}",
        )
    except PushBranchRenameError as err:
        logging.warning(err.message)
        try:
            rename_branch(repo["targetName"], "master", repo["localPath"])
        except RenameBranchError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch, but got an error pushing the change to remote, so the program tried to rename the branch back, but got another error! {err.message}",
            )
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, but got an error pushing th change to remote, so the program renamed the branch back. {err.message}",
        )
    except UpdateDefaultError as err:
        logging.warning(err.message)
        try:
            rename_branch(repo["targetName"], "master", repo["localPath"])
            push_setting_upstream(repo["localPath"], "master")
        except RenameBranchError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch and pushed the change to remote, but got an error changing the default branch on GitHub on GitHub, so the program tried to change the name back, but got an error! {err.message}",
            )
        except PushBranchRenameError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully renamed local branch and pushed the change to remote, but got an error changing the default branch on GitHub, so the program changed the name back locally, but got an error pushing the change to the remote! {err.message}",
            )
    except DeleteRemoteError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully renamed local branch, pushed the change to remote, and changed the default branch on GitHub, but got an error deleting the master branch on the remote! {err.message}",
        )


def remote_process_clone_repo(token, repo, localDirectory):
    """Mkdir if need be and clone the repo, then move the branch, push that
    upstream, change the default branch on GitHub, and delete remote master."""
    process = "'blast master on remote from cloned repo process'"
    try:
        mkdir_if_need_be(repo["ownerLogin"], localDirectory)
        clone_repo(repo["ownerLogin"], repo, localDirectory)
        clonedRepos.append(repo)
        newPath = f"{localDirectory}/master-blaster-{repo['ownerLogin']}/{repo['ownerLogin']}/{repo['name']}/"
        with open(f"{newPath}.git/config", "r") as configFile:
            if check_for_remote_or_remotes_and_get_url(configFile)[1] > 1:
                raise MultipleRemotesError()
        rename_branch("master", repo["targetName"], newPath)
        push_setting_upstream(repo["targetName"], newPath)
        update_default_branch(token, repo)
        delete_remote_branch("master", newPath)
    except MakeDirectoryError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Unable to make directory to clone repo into! {err.message}",
        )
    except CloneRepoError as err:
        logging.warning(err.message)
        raise ProcessError(
            process, repo["name"], f"Unable to clone repo! {err.message}"
        )
    except MultipleRemotesError as err:
        logging.warning(err.message)
        repo["status"] = "Multiple remotes found in git config file."
        raise ProcessError(process, repo["name"], err.message)
    except RenameBranchError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully cloned repo, but got an error trying to rename local branch! {err.message}",
        )
    except PushBranchRenameError as err:
        logging.warning(err.message)
        try:
            rename_branch(repo["targetName"], "master", newPath)
        except RenameBranchError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully cloned repo and renamed local branch, but got an error pushing the change to remote, so the program tried to rename the branch back, but then got another error! {err.message}",
            )
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully cloned repo and renamed local branch, but got an error pushing the change to remote, so the program renamed the branch back. {err.message}",
        )
    except UpdateDefaultError as err:
        logging.warning(err.message)
        try:
            rename_branch(repo["targetName"], "master", newPath)
            push_setting_upstream(newPath, "master")
        except RenameBranchError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully cloned repo, renamed local branch, and pushed the change to remote, but got an error changing the default branch on GitHub on GitHub, so the program tried to change the name back, but got an error! {err.message}",
            )
        except PushBranchRenameError as err:
            logging.warning(err.message)
            raise ProcessError(
                process,
                repo["name"],
                f"Successfully cloned repo, renamed local branch, and pushed the change to remote, but got an error changing the default branch on GitHub, so the program changed the name back locally, but got an error pushing the change to the remote! {err.message}",
            )
    except DeleteRemoteError as err:
        logging.warning(err.message)
        raise ProcessError(
            process,
            repo["name"],
            f"Successfully cloned repo, renamed local branch, pushed the change to remote, and changed the default branch on GitHub, but got an error deleting the master branch on the remote!  {err.message}",
        )


def run(dataWithOptions):
    """Run any actions to be run, and report and log!"""
    (
        username,
        token,
        repos,
        localDirectory,
        removeClones,
        gitNew,
    ) = dataWithOptions

    mvThirdToTargetLocalRepos = [
        repo
        for repo in repos
        if states["mvThirdToTarget"] in repo["status"]
        and repo.get("localPath")
        and not states["deleteMaster"] in repo["status"]
    ]
    mvThirdToTargetCloneRepos = [
        repo
        for repo in repos
        if states["mvThirdToTarget"] in repo["status"] and not repo.get("localPath")
    ]
    mvThirdToTargetAndDeleteRemoteMasterLocalRepos = [
        repo
        for repo in repos
        if states["mvThirdToTarget"] in repo["status"]
        and states["deleteMaster"] in repo["status"]
        and repo.get("localPath")
        and not repo.get("localHasMaster")
    ]
    mvThirdToTargetAndDeleteRemoteMasterCloneRepos = [
        repo
        for repo in repos
        if states["mvThirdToTarget"] in repo["status"]
        and states["deleteMaster"] in repo["status"]
        and not repo.get("localPath")
    ]
    mvThirdToTargetAndDeleteRemoteAndLocalMasters = [
        repo
        for repo in repos
        if states["mvThirdToTarget"] in repo["status"]
        and states["deleteMaster"] in repo["status"]
        and repo["hasMaster"]
        and repo.get("localHasMaster")
    ]
    mvThirdToTargetAndDeleteLocalMasters = [
        repo
        for repo in repos
        if states["mvThirdToTarget"] in repo["status"]
        and repo.get("localPath")
        and states["deleteMaster"] in repo["status"]
        and not repo["hasMaster"]
    ]
    deleteRemoteMasterLocalRepos = [
        repo
        for repo in repos
        if states["deleteMaster"] in repo["status"]
        and not states["mvThirdToTarget"] in repo["status"]
        and repo.get("localPath")
        and not repo.get("localHasMaster")
    ]
    deleteRemoteMasterCloneRepos = [
        repo
        for repo in repos
        if states["deleteMaster"] in repo["status"]
        and not repo.get("localPath")
        and not states["mvThirdToTarget"] in repo["status"]
    ]
    deleteLocalAndRemoteMasters = [
        repo
        for repo in repos
        if states["deleteMaster"]
        and repo.get("localHasMaster")
        and repo["hasMaster"]
        and not states["mvThirdToTarget"] in repo["status"]
    ]
    deleteLocalMasters = [
        repo
        for repo in repos
        if states["deleteMaster"] in repo["status"]
        and repo.get("localHasMaster")
        and not states["mvThirdToTarget"] in repo["status"]
    ]
    localUpdates = [
        repo for repo in repos if states["localUpdateProcess"] in repo["status"]
    ]
    remoteProcessLocalRepos = [
        repo
        for repo in repos
        if states["remoteProcess"] in repo["status"] and repo.get("localPath")
    ]
    remoteProcessCloneRepos = [
        repo
        for repo in repos
        if states["remoteProcess"] in repo["status"] and not repo.get("localPath")
    ]

    if len(mvThirdToTargetLocalRepos) > 0:
        for repo in mvThirdToTargetLocalRepos:
            try:
                mv_third_to_target_local_repo(token, repo)
            except ProcessError as err:
                repo["error"] = err.message
    if len(mvThirdToTargetCloneRepos) > 0:
        for repo in mvThirdToTargetCloneRepos:
            try:
                mv_third_to_target_clone_repo(token, repo, localDirectory)
            except ProcessError as err:
                repo["error"] = err.message
    if len(mvThirdToTargetAndDeleteRemoteMasterLocalRepos) > 0:
        for repo in mvThirdToTargetAndDeleteRemoteMasterLocalRepos:
            try:
                mv_third_to_target_and_delete_remote_master_local_repo(token, repo)
            except ProcessError as err:
                repo["error"] = err.message
    if len(mvThirdToTargetAndDeleteRemoteMasterCloneRepos) > 0:
        for repo in mvThirdToTargetAndDeleteRemoteMasterCloneRepos:
            try:
                mv_third_to_target_and_delete_remote_master_clone_repo(
                    token, repo, localDirectory
                )
            except ProcessError as err:
                repo["error"] = err.message
    if len(mvThirdToTargetAndDeleteRemoteAndLocalMasters) > 0:
        for repo in mvThirdToTargetAndDeleteRemoteAndLocalMasters:
            try:
                mv_third_to_target_and_delete_remote_and_local_master(token, repo)
            except ProcessError as err:
                repo["error"] = err.message
    if len(mvThirdToTargetAndDeleteLocalMasters) > 0:
        for repo in mvThirdToTargetAndDeleteLocalMasters:
            try:
                mv_third_to_target_and_delete_local_master(token, repo)
            except ProcessError as err:
                repo["error"] = err.message
    if len(deleteRemoteMasterLocalRepos) > 0:
        for repo in deleteRemoteMasterLocalRepos:
            try:
                delete_remote_master_local_repo(repo)
            except ProcessError as err:
                repo["error"] = err.message
    if len(deleteRemoteMasterCloneRepos) > 0:
        for repo in deleteRemoteMasterCloneRepos:
            try:
                delete_remote_master_clone_repo(token, repo, localDirectory)
            except ProcessError as err:
                repo["error"] = err.message
    if len(deleteLocalAndRemoteMasters) > 0:
        for repo in deleteLocalAndRemoteMasters:
            try:
                delete_remote_and_local_master(repo)
            except ProcessError as err:
                repo["error"] = err.message
    if len(deleteLocalMasters) > 0:
        for repo in deleteLocalMasters:
            try:
                delete_local_master(repo)
            except ProcessError as err:
                repo["error"] = err.message
    if len(localUpdates) > 0:
        for repo in localUpdates:
            try:
                local_update_process(repo)
            except ProcessError as err:
                repo["error"] = err.message
    if len(remoteProcessLocalRepos) > 0:
        for repo in remoteProcessLocalRepos:
            try:
                remote_process_local_repo(token, repo)
            except ProcessError as err:
                repo["error"] = err.message
    if len(remoteProcessCloneRepos) > 0:
        for repo in remoteProcessCloneRepos:
            try:
                remote_process_clone_repo(token, repo, localDirectory)
            except ProcessError as err:
                repo["error"] = err.message

    finalRepos = {
        "mvThirdToTargetLocalRepos": mvThirdToTargetLocalRepos,
        "mvThirdToTargetCloneRepos": mvThirdToTargetCloneRepos,
        "mvThirdToTargetAndDeleteRemoteMasterLocalRepos": mvThirdToTargetAndDeleteRemoteMasterLocalRepos,
        "mvThirdToTargetAndDeleteRemoteMasterCloneRepos": mvThirdToTargetAndDeleteRemoteMasterCloneRepos,
        "mvThirdToTargetAndDeleteRemoteAndLocalMasters": mvThirdToTargetAndDeleteRemoteAndLocalMasters,
        "mvThirdToTargetAndDeleteLocalMasters": mvThirdToTargetAndDeleteLocalMasters,
        "deleteRemoteMasterLocalRepos": deleteRemoteMasterLocalRepos,
        "deleteRemoteMasterCloneRepos": deleteRemoteMasterCloneRepos,
        "deleteLocalAndRemoteMasters": deleteLocalAndRemoteMasters,
        "deleteLocalMasters": deleteLocalMasters,
        "localUpdates": localUpdates,
        "remoteProcessLocalRepos": remoteProcessLocalRepos,
        "remoteProcessCloneRepos": remoteProcessCloneRepos,
    }

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
            git_new(repos[0]["targetName"])
        except GitNewError as err:
            logging.warning(err.message)
            gitNewError = True
            print(
                f"Error adding the git alias `git new` failed! You can run `git config --global alias.new '!git init && git symbolic-ref HEAD refs/heads/{repos[0]['targetname']}` to try again!"
            )
            pass

    report_on(
        repos,
        finalRepos,
        clonesRmAttempted,
        reposCloneDeletionError,
        gitNew,
        gitNewError,
    )
