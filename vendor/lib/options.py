from vendor.lib.reporting import repo_types_blurb
from vendor.lib.reporting import get_naming_mode
from vendor.lib.reporting import get_custom_name
from vendor.lib.reporting import get_custom_names
from vendor.lib.reporting import get_local_directory
from vendor.lib.reporting import get_remove_clones
from vendor.lib.reporting import get_git_new
from vendor.lib.actions.shell import get_local_repos
from vendor.lib.actions.network import check_remote_branches
from vendor.lib.actions.shell import check_local_branches
from vendor.lib.reporting import check_names


def apply_name(name, repos):
    for repo in repos:
        repo["targetName"] = name
    return repos


def check_branches(username, token, repos):
    """Get initial states of local and remote repos based on branch names."""
    repos = check_remote_branches(token, repos)
    localReposPresent = False
    for repo in repos:
        if repo.get("localPath"):
            localReposPresent = True
    if localReposPresent:
        repos = check_local_branches(repos)
    # print("check_branches")
    # print(repos)
    return repos


def get_options(data, testing):
    """Gather naming mode, name or names, catch errors, use local directories,
    starting local directory, removal of cloned repos, and git new alias."""
    username, token, repos = data

    repo_types_blurb()

    namingMode = ""
    name = ""

    main = "All primary branches renamed to 'main'."
    custom = "Choose name for all primary branches renamed to. "
    perRepo = "Choose a name for the primary branch for each repo."

    namingMode = get_naming_mode(main, custom, perRepo)

    if namingMode == main:
        name = "main"

    if namingMode == custom:
        name = get_custom_name()

    if namingMode == perRepo:
        repos = get_custom_names(repos)
    else:
        repos = apply_name(name, repos)

    localDirectory = get_local_directory(testing)
    removeClones = get_remove_clones(testing)
    gitNew = get_git_new(namingMode, perRepo, name, testing)

    # ! This is where get_options goes buck-wild.
    # * What we need are the check functions, a sort function,
    # * and a resolve naming conflicts function, *THEN* run()

    print("Checking repos ...")
    if localDirectory:
        repos = get_local_repos(repos, localDirectory, testing)
    repos = check_branches(username, token, repos)
    repos = check_names(repos)

    return username, token, repos, localDirectory, removeClones, gitNew
