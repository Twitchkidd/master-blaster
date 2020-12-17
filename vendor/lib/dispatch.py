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

clonedRepos = []


def mv_third_to_target_local(token, repo):
    """Rename third and push target upstream, rename default branch, delete remote third."""
    try:
        rename_branch(repo["default"], repo["targetName"], repo["localPath"])
        push_setting_upstream(repo["targetName"], repo["localPath"])
        update_default_branch(token, repo)
        delete_remote_branch(repo["default"], repo["localPath"])
    except Exception:
        pass
    # ! THIS IS BAD


def mv_third_to_target_clone(token, repo, localDirectory):
    """Clone branch, rename third and push target upstream, rename default branch, delete remote third."""
    error = mkdir_if_need_be(repo["ownerLogin"], localDirectory)
    if error:
        return error
    error = clone_repo(repo["ownerLogin"], token, repo, localDirectory)
    if error:
        return error
    clonedRepos.append(repo)
    newPath = f"{localDirectory}/master-blaster-{repo['ownerLogin']}/{repo['name']}/"
    error = rename_branch(repo["default"], repo["targetName"], newPath)
    if error:
        return error
    error = push_setting_upstream(repo["targetName"], newPath)
    if error:
        return error
    error = update_default_branch(token, repo)
    if error:
        return error
    return delete_remote_branch(repo["default"], newPath)


def mv_third_to_target_and_blast_local_master(token, repo, localDirectory):
    """Rename third and push target upstream, rename default branch, delete remote third, delete local master."""
    error = rename_branch(repo["default"], repo["targetName"], repo["localPath"])
    if error:
        return error
    error = push_setting_upstream(repo["targetName"], repo["localPath"])
    if error:
        return error
    error = update_default_branch(token, repo)
    if error:
        return error
    error = delete_remote_branch(repo["default"], repo["localPath"])
    if error:
        return error
    return delete_local_branch("master", repo["localPath"])


def delete_remote_process(token, repo, localDirectory):
    """Check if there's a local repo, then either clone or in-place push delete master."""
    if repo["localPath"]:
        return delete_remote_branch("master", repo["localPath"])
    else:
        error = mkdir_if_need_be(repo["ownerLogin"], localDirectory)
        if error:
            return error
        error = clone_repo(repo["ownerLogin"], token, repo, localDirectory)
        if error:
            return error
        clonedRepos.append(repo)
        newPath = (
            f"{localDirectory}/master-blaster-{repo['ownerLogin']}/{repo['name']}/"
        )
        return delete_remote_branch(repo["default"], newPath)


def delete_local_and_remote(repo):
    """Delete remote and local master branches."""
    error = delete_remote_branch("master", repo["localPath"])
    if error:
        return error
    return delete_local_branch("master", repo["localPath"])


def local_process(repo):
    """To sync up a local repo whose remote has been blasted, check out master, move it to target,
    fetch, unset the upstream, set the upstream, and update the symbolic ref."""
    error = checkout("master", repo["localPath"])
    if error:
        return error
    error = rename_branch("master", repo["targetName"], repo["localPath"])
    if error:
        return error
    error = fetch(repo["localPath"])
    if error:
        return error
    error = unset_upstream(repo["localPath"])
    if error:
        return error
    error = set_upstream(repo["targetName"], repo["localPath"])
    if error:
        return error
    return update_symbolic_ref(repo["targetName"], repo["localPath"])


def remote_process_local(token, repo):
    """Move the branch, push that upstream, change the default branch, and delete remote master."""
    print(repo)
    error = rename_branch("master", repo["targetName"], repo["localPath"])
    if error:
        return error
    error = push_setting_upstream(repo["targetName"], repo["localPath"])
    if error:
        return error
    error = update_default_branch(token, repo)
    if error:
        return error
    return delete_remote_branch("master", repo["localPath"])


def remote_process_clone(token, repo, localDirectory):
    """Mkdir if need be and clone the repo, then move the branch, push that upstream, change the
    default branch, and delete remote master."""
    error = mkdir_if_need_be(repo["ownerLogin"], localDirectory)
    if error:
        return error
    error = clone_repo(repo["ownerLogin"], token, repo, localDirectory)
    if error:
        return error
    clonedRepos.append(repo)
    newPath = f"{localDirectory}/master-blaster-{repo['ownerLogin']}/{repo['name']}/"
    error = rename_branch("master", repo["targetName"], newPath)
    if error:
        return error
    error = push_setting_upstream(repo["targetName"], newPath)
    if error:
        return error
    error = update_default_branch(token, repo)
    if error:
        return error
    return delete_remote_branch("master", newPath)


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
            error = mv_third_to_target_local(token, repo)
            if error:
                optionRepos["reposMvThirdToTargetLocal"]["errors"].append([repo, error])

    if len(optionRepos["reposMvThirdToTargetClone"]["repos"]) > 0:
        for repo in optionRepos["reposMvThirdToTargetClone"]["repos"]:
            error = mv_third_to_target_clone(token, repo, localDirectory)
            if error:
                optionRepos["reposMvThirdToTargetClone"]["errors"].append([repo, error])

    if len(optionRepos["reposMvThirdToTargetAndBlastLocalMaster"]["repos"]) > 0:
        for repo in optionRepos["reposMvThirdToTargetAndBlastLocalMaster"]["repos"]:
            error = mv_third_to_target_and_blast_local_master(repo)
            if error:
                optionRepos["reposMvThirdToTargetAndBlastLocalMaster"]["errors"].append(
                    [repo, error]
                )

    if len(optionRepos["reposDeleteRemote"]["repos"]) > 0:
        for repo in optionRepos["reposDeleteRemote"]["repos"]:
            error = delete_remote_process("master", repo["localPath"])
            if error:
                optionRepos["reposDeleteRemote"]["errors"].append([repo, error])

    if len(optionRepos["reposDeleteLocal"]["repos"]) > 0:
        for repo in optionRepos["reposDeleteLocal"]["repos"]:
            error = delete_local_branch("master", repo["localPath"])
            if error:
                optionRepos["reposDeleteLocal"]["errors"].append([repo, error])

    if len(optionRepos["reposDeleteLocalAndRemote"]["repos"]) > 0:
        for repo in optionRepos["reposDeleteLocalAndRemote"]["repos"]:
            error = delete_local_and_remote(repo)
            if error:
                optionRepos["reposDeleteLocalAndRemote"]["errors"].append([repo, error])

    if len(optionRepos["reposLocalProcess"]["repos"]) > 0:
        for repo in optionRepos["reposLocalProcess"]["repos"]:
            error = local_process(repo)
            if error:
                optionRepos["reposLocalProcess"]["errors"].append([repo, error])

    if len(reposRemoteProcessLocal) > 0:
        for repo in reposRemoteProcessLocal:
            error = remote_process_local(token, repo)
            if error:
                reposRemoteProcessLocal["errors"].append([repo, error])

    if len(reposRemoteProcessClone) > 0:
        for repo in reposRemoteProcessClone:
            error = remote_process_clone(token, repo, localDirectory)
            if error:
                reposRemoteProcessClone["errors"].append([repo, error])

    clonesRmAttempted = False
    reposCloneDeletionError = False
    if removeClones and len(clonedRepos) > 0:
        clonesRmAttempted = True
        reposCloneDeletionError = rm_clone_folder(username, localDirectory)

    gitNewError = False
    if gitNew:
        gitNewError = git_new

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
