

# dispatch #
# * Run actions through dispatch.
# * The run function should take a token, username,
# * and repos list, a set of options, and the
# * testing boolean, and do the appropriate set of actions. * #

def run(data, options, testing):
    """We assume that the wizard has managed logical errors in our data already,
    and that we have ready for local, ready for remote, already blasted, or an
    error message/grouping."""
    Run the local process on any repos ready for local.

    Run the remote process on any repos ready for remote.

    Remove any cloned repos if that option is enabled.

    Add alias git new if that option is enabled.

    Check for any stray master branches.

    If there are, ask about that, if so, chop em.
    # logging #
    # reporting #
    Collect any errors for logging and reporting.


from pathlib import Path
from subprocess import Popen, PIPE

# * Any actions should be run through dispatch.
# * The run function should take a token, a set
# * of options, and the testing boolean, and do
# * the appropriate set of actions. * #

# Yay this works!

# * ``` From u/merfi on SO, added a path param ``` * #


def get_active_branch_name(path):
    head_dir = Path(path) / ".git" / "HEAD"
    with head_dir.open("r") as f:
        content = f.read().splitlines()

    for line in content:
        if line[0:4] == "ref:":
            return line.partition("refs/heads/")[2]


def run(token, options, testing):
    currentBranch = ""
    if testing:
        if f"{Path.home()}/Code/master-blaster" == f"{Path.cwd()}":
            currentBranch = get_active_branch_name(f"{Path.cwd()}")

    # This should run last
    # ! Testing! #
    if len(currentBranch) > 0:
        Popen(["git", "checkout", f"{currentBranch}"], stdout=PIPE, stderr=PIPE)

    def getToken():
        tokenConfirmed = False
        while not tokenConfirmed:
            customTokenResponse = questionary.text(tokenPrompt(tokenType)).ask()
            if customTokenResponse == "":
                print("Please enter the token!")
                continue
            else:
                token = customTokenResponse
                tokenConfirmed = True
                continue
        # ! Testing! #
        token = tokenRepoScope
        # # token = "fermf"
        return token