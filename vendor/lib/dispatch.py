from vendor.lib.actions.shell import renameBranch
from vendor.lib.actions.shell import pushSettingUpstream
from vendor.lib.actions.network import updateDefaultBranch
from vendor.lib.actions.shell import deleteRemoteBranch
from vendor.lib.actions.shell import mkdirIfNeedBe
from vendor.lib.actions.network import cloneRepo

# from vendor.lib.actions.network import mvThirdToTargetAndBlastLocalMaster
from vendor.lib.actions.network import deleteRemote
from vendor.lib.actions.shell import deleteLocal

# from vendor.lib.actions.network import deleteLocalAndRemote
from vendor.lib.actions.shell import localProcess
from vendor.lib.reporting import reportOn

# dispatch #
# * Run actions through dispatch.
# * The run function should take a token, username,
# * and repos list, a set of options, and the
# * testing boolean, and do the appropriate set of actions. * #


def mvThirdToTargetLocal(token, repo):
    """Rename third and push target upstream, rename default branch, delete remote third."""
    renameBranch(repo["default"], repo["targetName"], repo["localPath"])
    error = pushSettingUpstream(repo["targetName"], repo["localPath"])
    if error:
        return error
    error = updateDefaultBranch(token, repo)
    if error:
        return error
    error = deleteRemoteBranch(repo["default"], repo["localPath"])
    return error


def mvThirdToTargetClone(username, token, repo, localDirectory):
    """Clone branch, rename third and push target upstream, rename default branch, delete remote third."""
    error = mkdirIfNeedBe(username, localDirectory)
    if error:
        return error
    error = cloneRepo(username, token, repo, localDirectory)
    if error:
        return error
    newPath = f"{localDirectory}/master-blaster-{username}/{repo['name']}/"
    error = 


def mvThirdToTargetAndBlastLocalMaster(repo):
    """Handle this scenario."""


def deleteLocalAndRemote(repo):
    """Handle this scenario."""


def remoteProcessLocal(repo):
    """Handle this scenario."""


def remoteProcessClone(repo):
    """Handle this scenario."""


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
            error = mvThirdToTargetClone(username, token, repo, localDirectory)
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
            error = deleteRemote(repo)
            if error:
                optionRepos.reposDeleteRemote.errors.append([repo, error])

    if not optionRepos.reposDeleteLocal.pending:
        for repo in optionRepos.reposDeleteLocal.repos:
            error = deleteLocal(repo)
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
        error = remoteProcessLocal(repo)
        if error:
            reposRemoteProcessLocal.errors.append([repo, error])

    for repo in reposRemoteProcessClone:
        error = remoteProcessClone(repo)
        if error:
            reposRemoteProcessClone.errors.append([repo, error])

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

    reportOn(finalRepos)