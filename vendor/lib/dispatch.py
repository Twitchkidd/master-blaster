from vendor.lib.actions.shell import renameBranch
from vendor.lib.actions.shell import pushSettingUpstream
from vendor.lib.actions.network import updateDefaultBranch
from vendor.lib.actions.shell import deleteRemoteBranch
from vendor.lib.actions.shell import mkdirIfNeedBe
from vendor.lib.actions.shell import cloneRepo
from vendor.lib.actions.shell import deleteLocalBranch
from vendor.lib.actions.shell import checkout
from vendor.lib.actions.shell import fetch
from vendor.lib.actions.shell import unsetUpstream
from vendor.lib.actions.shell import setUpstream
from vendor.lib.actions.shell import updateSymbolicRef
from vendor.lib.actions.shell import rmCloneFolder
from vendor.lib.actions.shell import gitNew
from vendor.lib.reporting import reportOn

# dispatch #
# * Run actions through dispatch.
# * The run function should take a token, username,
# * and repos list, a set of options, and the
# * testing boolean, and do the appropriate set of actions. * #

clonedRepos = []


def mvThirdToTargetLocal(token, repo):
    """Rename third and push target upstream, rename default branch, delete remote third."""
    error = renameBranch(repo["default"], repo["targetName"], repo["localPath"])
    if error:
        return error
    error = pushSettingUpstream(repo["targetName"], repo["localPath"])
    if error:
        return error
    error = updateDefaultBranch(token, repo)
    if error:
        return error
    return deleteRemoteBranch(repo["default"], repo["localPath"])


def mvThirdToTargetClone(token, repo, localDirectory):
    """Clone branch, rename third and push target upstream, rename default branch, delete remote third."""
    error = mkdirIfNeedBe(repo["ownerLogin"], localDirectory)
    if error:
        return error
    error = cloneRepo(repo["ownerLogin"], token, repo, localDirectory)
    if error:
        return error
    clonedRepos.append(repo)
    newPath = f"{localDirectory}/master-blaster-{repo['ownerLogin']}/{repo['name']}/"
    error = renameBranch(repo["default"], repo["targetName"], newPath)
    if error:
        return error
    error = pushSettingUpstream(repo["targetName"], newPath)
    if error:
        return error
    error = updateDefaultBranch(token, repo)
    if error:
        return error
    return deleteRemoteBranch(repo["default"], newPath)


def mvThirdToTargetAndBlastLocalMaster(token, repo, localDirectory):
    """Rename third and push target upstream, rename default branch, delete remote third, delete local master."""
    error = renameBranch(repo["default"], repo["targetName"], repo["localPath"])
    if error:
        return error
    error = pushSettingUpstream(repo["targetName"], repo["localPath"])
    if error:
        return error
    error = updateDefaultBranch(token, repo)
    if error:
        return error
    error = deleteRemoteBranch(repo["default"], repo["localPath"])
    if error:
        return error
    return deleteLocalBranch("master", repo["localPath"])


def deleteRemoteProcess(token, repo, localDirectory):
    """Check if there's a local repo, then either clone or in-place push delete master."""
    if repo["localPath"]:
        return deleteRemoteBranch("master", repo["localPath"])
    else:
        error = mkdirIfNeedBe(repo["ownerLogin"], localDirectory)
        if error:
            return error
        error = cloneRepo(repo["ownerLogin"], token, repo, localDirectory)
        if error:
            return error
        clonedRepos.append(repo)
        newPath = (
            f"{localDirectory}/master-blaster-{repo['ownerLogin']}/{repo['name']}/"
        )
        return deleteRemoteBranch(repo["default"], newPath)


def deleteLocalAndRemote(repo):
    """Delete remote and local master branches."""
    error = deleteRemoteBranch("master", repo["localPath"])
    if error:
        return error
    return deleteLocalBranch("master", repo["localPath"])


def localProcess(repo):
    """To sync up a local repo whose remote has been blasted, check out master, move it to target,
    fetch, unset the upstream, set the upstream, and update the symbolic ref."""
    error = checkout("master", repo["localPath"])
    if error:
        return error
    error = renameBranch("master", repo["targetName"], repo["localPath"])
    if error:
        return error
    error = fetch(repo["localPath"])
    if error:
        return error
    error = unsetUpstream(repo["localPath"])
    if error:
        return error
    error = setUpstream(repo["targetName"], repo["localPath"])
    if error:
        return error
    return updateSymbolicRef(repo["targetName"], repo["localPath"])


def remoteProcessLocal(token, repo):
    """Move the branch, push that upstream, change the default branch, and delete remote master."""
    error = renameBranch("master", repo["targetName"], repo["localPath"])
    if error:
        return error
    error = pushSettingUpstream(repo["targetName"], repo["localPath"])
    if error:
        return error
    error = updateDefaultBranch(token, repo)
    if error:
        return error
    return deleteRemoteBranch("master", repo["localPath"])


def remoteProcessClone(token, repo, localDirectory):
    """Mkdir if need be and clone the repo, then move the branch, push that upstream, change the
    default branch, and delete remote master."""
    error = mkdirIfNeedBe(repo["ownerLogin"], localDirectory)
    if error:
        return error
    error = cloneRepo(repo["ownerLogin"], token, repo, localDirectory)
    if error:
        return error
    clonedRepos.append(repo)
    newPath = f"{localDirectory}/master-blaster-{repo['ownerLogin']}/{repo['name']}/"
    error = renameBranch("master", repo["targetName"], newPath)
    if error:
        return error
    error = pushSettingUpstream(repo["targetName"], newPath)
    if error:
        return error
    error = updateDefaultBranch(token, repo)
    if error:
        return error
    return deleteRemoteBranch("master", newPath)


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

    for repo in repos:
        if repo["status"] == states.remoteProcessLocal:
            reposRemoteProcessLocal.repos.append(repo)
        if repo["status"] == states.remoteProcessClone:
            reposRemoteProcessClone.repos.append(repo)
        if repo["status"] == states.alreadyBlasted:
            reposAlreadyBlasted.repos.append(repo)
        if repo["status"] == states.pathUnclear:
            reposPathUnclear.repos.append(repo)
        if repo["status"] == states.folderError:
            reposFolderError.repos.append(repo)

    if not optionRepos.reposMvThirdToTargetLocal.pending:
        for repo in optionRepos.reposMvThirdToTargetLocal.repos:
            error = mvThirdToTargetLocal(token, repo)
            if error:
                optionRepos.reposMvThirdToTargetLocal.errors.append([repo, error])

    if not optionRepos.reposMvThirdToTargetClone.pending:
        for repo in optionRepos.reposMvThirdToTargetClone.repos:
            error = mvThirdToTargetClone(token, repo, localDirectory)
            if error:
                optionRepos.reposMvThirdToTargetClone.errors.append([repo, error])

    if not optionRepos.reposMvThirdToTargetAndBlastLocalMaster.pending:
        for repo in optionRepos.reposMvThirdToTargetAndBlastLocalMaster.repos:
            error = mvThirdToTargetAndBlastLocalMaster(repo)
            if error:
                optionRepos.reposMvThirdToTargetAndBlastLocalMaster.errors.append(
                    [repo, error]
                )

    if not optionRepos.reposDeleteRemote.pending:
        for repo in optionRepos.reposDeleteRemote.repos:
            error = deleteRemoteProcess("master", repo["localPath"])
            if error:
                optionRepos.reposDeleteRemote.errors.append([repo, error])

    if not optionRepos.reposDeleteLocal.pending:
        for repo in optionRepos.reposDeleteLocal.repos:
            error = deleteLocalBranch("master", repo["localPath"])
            if error:
                optionRepos.reposDeleteLocal.errors.append([repo, error])

    if not optionRepos.reposDeleteLocalAndRemote.pending:
        for repo in optionRepos.reposDeleteLocalAndRemote.repos:
            error = deleteLocalAndRemote(repo)
            if error:
                optionRepos.reposDeleteLocalAndRemote.errors.append([repo, error])

    if not optionRepos.reposLocalProcess.pending:
        for repo in optionRepos.reposLocalProcess.repos:
            error = localProcess(repo)
            if error:
                optionRepos.reposLocalProcess.errors.append([repo, error])

    for repo in reposRemoteProcessLocal:
        error = remoteProcessLocal(token, repo)
        if error:
            reposRemoteProcessLocal.errors.append([repo, error])

    for repo in reposRemoteProcessClone:
        error = remoteProcessClone(token, repo, localDirectory)
        if error:
            reposRemoteProcessClone.errors.append([repo, error])

    clonesRmAttempted = False
    reposCloneDeletionError = False
    if removeClones and len(clonedRepos) > 0:
        clonesRmAttempted = True
        reposCloneDeletionError = rmCloneFolder(username, localDirectory)

    gitNewError = False
    if gitNew:
        gitNewError = gitNew

    finalRepos = {
        "reposMvThirdToTargetLocal": optionRepos.reposMvThirdToTargetLocal,
        "reposMvThirdToTargetClone": optionRepos.reposMvThirdToTargetClone,
        "reposMvThirdToTargetAndBlastLocalMaster": optionRepos.reposMvThirdToTargetAndBlastLocalMaster,
        "reposDeleteRemote": optionRepos.reposDeleteRemote,
        "reposDeleteLocal": optionRepos.reposDeleteLocal,
        "reposDeleteLocalAndRemote": optionRepos.reposDeleteLocalAndRemote,
        "reposLocalProcess": optionRepos.reposLocalProcess,
        "reposRemoteProcessLocal": reposRemoteProcessLocal,
        "reposRemoteProcessClone": reposRemoteProcessClone,
        "reposAlreadyBlasted": reposAlreadyBlasted,
        "reposPathUnclear": reposPathUnclear,
        "reposFolderError": reposFolderError,
    }

    reportOn(
        finalRepos, clonesRmAttempted, reposCloneDeletionError, gitNew, gitNewError
    )
