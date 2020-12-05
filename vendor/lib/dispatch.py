from vendor.lib.actions.network import mvThirdToTargetLocal

# dispatch #
# * Run actions through dispatch.
# * The run function should take a token, username,
# * and repos list, a set of options, and the
# * testing boolean, and do the appropriate set of actions. * #


def run(dataWithOptions):
    """Run any actions to be run, and report and log!"""
    username, token, repos, localDirectory, removeClones, gitNew = dataWithOptions

    states = {
        "pendingMvThirdToTargetLocal": "Do you want to mv third to target? Local repo",
        "mvThirdToTargetLocal": "Move third to target, local repo.",
        "pendingMvThirdToTargetClone": "Do you want to mv third to target? Clone repo",
        "MvThirdToTargetClone": "Move third to target, clone repo.",
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

    reposPendingMvThirdToTargetLocal = []
    reposMvThirdToTargetLocal = []
    reposPendingMvThirdToTargetClone = []
    reposMvThirdToTargetClone = []
    reposPendingMvThirdToTargetAndBlastLocalMaster = []
    reposMvThirdToTargetAndBlastLocalMaster = []
    reposPendingDeleteRemote = []
    reposDeleteRemote = []
    reposPendingDeleteLocal = []
    reposDeleteLocal = []
    reposPendingDeleteLocalAndRemote = []
    reposDeleteLocalAndRemote = []
    reposPendingLocalProcess = []
    reposLocalProcess = []
    reposRemoteProcessLocal = []
    reposRemoteProcessClone = []
    reposAlreadyBlasted = []
    reposPathUnclear = []
    reposFolderError = []

    for repo in repos:
        if repo["status"] == states.pendingMvThirdToTargetLocal:
            reposPendingMvThirdToTargetLocal.append(repo)
        if repo["status"] == states.mvThirdToTargetLocal:
            reposMvThirdToTargetLocal.append(repo)
        if repo["status"] == states.pendingMvThirdToTargetClone:
            reposPendingMvThirdToTargetClone.append(repo)
        if repo["status"] == states.mvThirdToTargetClone:
            reposMvThirdToTargetClone.append(repo)
        if repo["status"] == states.pendingMvThirdToTargetAndBlastLocalMaster:
            reposPendingMvThirdToTargetAndBlastLocalMaster.append(repo)
        if repo["status"] == states.mvThirdToTargetAndBlastLocalMaster:
            reposMvThirdToTargetAndBlastLocalMaster.append(repo)
        if repo["status"] == states.pendingDeleteRemote:
            reposPendingDeleteRemote.append(repo)
        if repo["status"] == states.deleteRemote:
            reposDeleteRemote.append(repo)
        if repo["status"] == states.pendingDeleteLocal:
            reposPendingDeleteLocal.append(repo)
        if repo["status"] == states.deleteLocal:
            reposDeleteLocal.append(repo)
        if repo["status"] == states.pendingDeleteLocalAndRemote:
            reposPendingDeleteLocalAndRemote.append(repo)
        if repo["status"] == states.deleteLocalAndRemote:
            reposDeleteLocalAndRemote.append(repo)
        if repo["status"] == states.pendingLocalProcess:
            reposPendingLocalProcess.append(repo)
        if repo["status"] == states.localProcess:
            reposLocalProcess.append(repo)
        if repo["status"] == states.remoteProcessLocal:
            reposRemoteProcessLocal.append(repo)
        if repo["status"] == states.remoteProcessClone:
            reposRemoteProcessClone.append(repo)
        if repo["status"] == states.alreadyBlasted:
            reposAlreadyBlasted.append(repo)
        if repo["status"] == states.pathUnclear:
            reposPathUnclear.append(repo)
        if repo["status"] == states.folderError:
            reposFolderError.append(repo)

    if len(reposMvThirdToTargetLocal) > 0:
        for repo in reposMvThirdToTargetLocal:
            mvThirdToTargetLocal(repo)
