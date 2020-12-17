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
from vendor.lib.actions.shell_exceptions import RenameBranchError
from vendor.lib.actions.shell_exceptions import PushBranchRenameError
from vendor.lib.actions.shell_exceptions import UpdateDefaultError
from vendor.lib.actions.shell_exceptions import DeleteRemoteError
from vendor.lib.actions.shell_exceptions import MakeDirectoryError
from vendor.lib.actions.shell_exceptions import CloneRepoError

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
    """Rename third and push target upstream, rename default branch, delete remote third."""
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
            f"Tried to rename branch locally, but couldn't!",
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
                f"Renamed locally, but couldn't push change to remote, so we tried to rename the branch back, but couldn't!",
            )
        raise ProcessError(
            process,
            repo["name"],
            f"Renamed locally, but couldn't push change to remote, so we renamed the branch back",
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
                f"Renamed locally, pushed change to remote, but couldn't change the default branch, so we tried to change the name back, but couldn't!",
            )
        except PushBranchRenameError as err:
            logging.warning(err)
            raise ProcessError(
                process,
                repo["name"],
                f"Renamed locally, pushed change to remote, but couldn't change the default branch, so we changed the name back, but couldn't push it to the remote!",
            )
    except DeleteRemoteError as err:
        logging.warning(err)
        raise ProcessError(
            process,
            repo["name"],
            f"Renamed locally, pushed change to remote, changed the default branch, but couldn't delete {repo['default']} branch on the remote!",
        )


def mv_third_to_target_clone(token, repo, localDirectory):
    """Clone branch, rename third and push target upstream, rename default branch, delete remote third."""
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
            f"Unable to make directory to clone {repo['name']} into! {err}",
        )
    except CloneRepoError as err:
        logging.warning(err)
        raise ProcessError(
            process, repo["name"], f"Unable to clone {repo['name']}! {err}"
        )
    # ! HERE


def mv_third_to_target_and_blast_local_master(token, repo, localDirectory):
    """Rename third and push target upstream, rename default branch, delete remote third, delete local master."""
    try:
        rename_branch(repo["default"], repo["targetName"], repo["localPath"])
        push_setting_upstream(repo["targetName"], repo["localPath"])
        update_default_branch(token, repo)
        delete_remote_branch(repo["default"], repo["localPath"])
        delete_local_branch("master", repo["localPath"])
    except Exception:
        pass  # ! HERE


def delete_remote_process(token, repo, localDirectory):
    """Check if there's a local repo, then either clone or in-place push delete master."""
    if repo["localPath"]:
        try:
            delete_remote_branch("master", repo["localPath"])
        except DeleteRemoteError as err:
            logging.warning(err)
            raise ProcessError(
                "'delete remote branch from local repo process'",
                repo["localPath"],
                f"Unable to delete remote branch of {repo['name']}! {err}",
            )
    else:
        process = "somthing"  # ! HERE
        try:
            mkdir_if_need_be(repo["ownerLogin"], localDirectory)
            clone_repo(repo["ownerLogin"], token, repo, localDirectory)
            clonedRepos.append(repo)
            newPath = (
                f"{localDirectory}/master-blaster-{repo['ownerLogin']}/{repo['name']}/"
            )
            delete_remote_branch(repo["default"], newPath)
        except Exception:
            pass  # ! HERE


def delete_local_and_remote(repo):
    """Delete remote and local master branches."""
    process = "'delete remote and local master branches process'"
    try:
        delete_remote_branch("master", repo["localPath"])
        delete_local_branch("master", repo["localPath"])
    except Exception:
        pass  # ! HERE


def local_process(repo):
    """To sync up a local repo whose remote has been blasted, check out master, move it to target,
    fetch, unset the upstream, set the upstream, and update the symbolic ref."""
    process = "Something"  # ! HERE
    try:
        checkout("master", repo["localPath"])
        rename_branch("master", repo["targetName"], repo["localPath"])
        fetch(repo["localPath"])
        unset_upstream(repo["localPath"])
        set_upstream(repo["targetName"], repo["localPath"])
        update_symbolic_ref(repo["targetName"], repo["localPath"])
    except Exception:
        pass  # ! HERE


def remote_process_local(token, repo):
    """Move the branch, push that upstream, change the default branch, and delete remote master."""
    process = "something"  # ! HERE
    try:
        rename_branch("master", repo["targetName"], repo["localPath"])
        push_setting_upstream(repo["targetName"], repo["localPath"])
        update_default_branch(token, repo)
        delete_remote_branch("master", repo["localPath"])
    except Exception:
        pass  # ! HERE


def remote_process_clone(token, repo, localDirectory):
    """Mkdir if need be and clone the repo, then move the branch, push that upstream, change the
    default branch, and delete remote master."""
    process = "something"  # ! HERE
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
    except Exception:
        pass  # ! HERE


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
    reposCloneDeletionError = False
    if removeClones and len(clonedRepos) > 0:
        clonesRmAttempted = True
        try:
            rm_clone_folder(username, localDirectory)
        except ProcessError as err:
            reposCloneDeletionError = err.message

    gitNewError = False
    if gitNew:
        try:
            git_new
        except ProcessError as err:
            getNewError = err.message

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
