# * Add the `git new` alias! * #


def runGitNew():
    gitNewGcg = Popen(
        [
            "git",
            "config",
            "--global",
            "alias.new",
            f"!git init && git symbolic-ref HEAD refs/heads/{name}",
        ],
        stdout=PIPE,
        stderr=PIPE,
    )
    gitNewGcgExitCode = processLogger(
        f"git config --global alias.new '!git init && git symbolic-ref HEAD refs/heads/{name}'",
        gitNewGcg,
    )[2]
    if gitNewGcgExitCode == 0:
        print(f"Git alias git new: initalize git repo with HEAD ref refs/heads/{name}")
    else:
        print("Git alias add failed, see log file.")


if gitNew:
    runGitNew()