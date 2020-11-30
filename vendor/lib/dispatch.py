from pathlib import Path
from subprocess import Popen, PIPE
from vendor.lib.options import sayHi

# Yay this works!

# * ``` From u/merfi on SO, added a path param ``` * #


def get_active_branch_name(path):
    head_dir = Path(path) / ".git" / "HEAD"
    with head_dir.open("r") as f:
        content = f.read().splitlines()

    for line in content:
        if line[0:4] == "ref:":
            return line.partition("refs/heads/")[2]


def run(token, testing):
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