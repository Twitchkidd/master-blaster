#!/usr/bin/env python

from subprocess import Popen, PIPE
from pathlib import Path
# import logging
# import requests
# import json

# # ! ``` Placeholder variables for the testing tokens! ``` ! #
# # ! Testing! #
# tokenRepoScope = ""

# # ! Testing! #
# with open("./repo.txt", 'r') as repoF:
#     tokenRepoScope = repoF.read(40)

# # * ``` Write to a new or existing log file! ``` * #
# # ! Testing! #
# # filemode='w' will not append to the file, it'll write over
# logging.basicConfig(filename='testInfo.log', filemode='w',
#                     level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
# print("""
#     Log file found at ./testInfo.log!
# """)
# logging.info("Creating a log file!!")


def main():
    # dicticle = {}
    # result = subprocess.run(["git", "branch"], universal_newlines=True,
    #                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # print(result.stdout)
    # # print(type(result.stdout))
    # # print(result.stderr)
    # # print(result.returncode)
    # dicticle['yay'] = 'dev' in result.stdout
    # print(dicticle["yay"])
    # if None:
    #     print(dicticle.get('nay'))
    # headers = {"Authorization": 'token ' + tokenRepoScope}
    # params = json.dumps({"default_branch": "main"})
    # response = requests.patch("https://api.github.com/repos/Twitchkidd/master-blaster",
    #                           data=params, headers=headers)
    # print(response.status_code)
    # processOne = subprocess.Popen(
    #     ["mkdir", "-pv", "/Users/gareth/Code/master-blaster-Twitchkidd/"], cwd="/Users/gareth/Code", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # stdoutOne, stderrOne = processOne.communicate()
    # print(f"stdoutOne: {stdoutOne}")
    # print(f"stderrOne: {stderrOne}")
    # processTwo = subprocess.Popen(
    #     ["git", "clone", "https://github.com/Twitchkidd/dep-server.git", "./dep-server/"], cwd="/Users/gareth/Code/master-blaster-Twitchkidd/", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # stdoutTwo, stderrTwo = processTwo.communicate()
    # print(f"stdoutTwo: {stdoutTwo}")
    # print(f"stderrTwo: {stderrTwo}")
    # processThree = subprocess.Popen(
    #     ["git", "branch", "-m", "master", "main"], cwd="/Users/gareth/Code/master-blaster-Twitchkidd/dep-server/", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # stdoutThree, stderrThree = processThree.communicate()
    # print(f"stdoutThree: {stdoutThree}")
    # print(f"stderrThree: {stderrThree}")
    # processFour = subprocess.Popen(
    #     ["git", "push", "-u", "origin", "main"], cwd="/Users/gareth/Code/master-blaster-Twitchkidd/dep-server/", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # stdoutFour, stderrFour = processFour.communicate()
    # print(f"stdoutFour: {stdoutFour}")
    # print(f"stderrFour: {stderrFour}")
    # processFive = subprocess.Popen(
    #     ["rm", "-dfRv", "/Users/gareth/Code/master-blaster-Twitchkidd/"], cwd="/Users/gareth/Code/", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # stdoutFive, stderrFive = processFive.communicate()
    # print(f"stdoutFive: {stdoutFive}")
    # print(f"stderrFive: {stderrFive}")
    # def constructPatchDefaultUrl(repo):
    #     return f"{GITHUB_API}/repos/{repo['owner-login']}/{repo['name']}"
    # url = "https://api.github.com/repos/Twitchkidd/dep-server"
    # params = json.dumps({"default_branch": "main"})
    # patchDefaultResponse = requests.patch(url, data=params, headers=headers)
    # if patchDefaultResponse.status_code >= 400:
    #     # logging.warning(f"Response status: {patchDefaultResponse.status_code}")
    #     print(
    #         f"Network error! Status code: {patchDefaultResponse.status_code} {patchDefaultResponse.json()}")
    # else:
    #     print(
    #         f"Default branch for dep-server updated to main!")
    # logging.info(
    #     f"Default branch for {repo['htmlUrl']} updated to {repo['primaryBranchName']}.")
    # processSix = subprocess.Popen(
    #     ["git", "push", "origin", "--delete", "master"], cwd="/Users/gareth/Code/master-blaster-Twitchkidd/dep-server/", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # stdoutSix, stderrSix = processSix.communicate()
    # print(f"stdoutSix: {stdoutSix}")
    # print(f"stderrSix: {stderrSix}")
    # processFive = subprocess.Popen(
    #     ["rm", "-dfRv", "/Users/gareth/Code/master-blaster-Twitchkidd/master-blaster-Twitchkidd/"], cwd="/Users/gareth/Code/", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # stdoutFive, stderrFive = processFive.communicate()
    # print(f"stdoutFive: {stdoutFive}")
    # print(f"stderrFive: {stderrFive}")
    # repo = {'primaryBranchName': 'main'}
    # localRepo = {'path': '/Users/gareth/Code/localCloned'}
    # localProcessGcm = subprocess.Popen(["git", "checkout", "master"], cwd=f"{localRepo['path']}", universal_newlines=True,
    #                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # logging.info(localProcessGcm.stdout)
    # logging.info(f"cwd={localRepo['path']}: git checkout master")
    # if localProcessGcm.stderr:
    #     logging.warning(localProcessGcm.stderr)
    # localProcessGbm = subprocess.Popen(["git", "branch", "-m", "master", repo['primaryBranchName']], cwd=f"{localRepo['path']}", universal_newlines=True,
    #                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # logging.info(
    #     f"cwd={localRepo['path']}: git branch -m master {repo['primaryBranchName']}")
    # logging.info(localProcessGbm.stdout)
    # if localProcessGbm.stderr:
    #     logging.warning(localProcessGbm.stderr)
    # localProcessGf = subprocess.Popen(["git", "fetch"], cwd=f"{localRepo['path']}", universal_newlines=True,
    #                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # logging.info(localProcessGf.stdout)
    # logging.info(f"cwd={localRepo['path']}: git fetch")
    # if localProcessGf.stderr:
    #     logging.warning(localProcessGf.stderr)
    # localProcessGbuu = subprocess.Popen(["git", "branch", "--unset-upstream"], cwd=f"{localRepo['path']}", universal_newlines=True,
    #                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # logging.info(localProcessGbuu.stdout)
    # logging.info(
    #     f"cwd={localRepo['path']}: git branch --unset-upstream")
    # if localProcessGbuu.stderr:
    #     logging.warning(localProcessGbuu.stderr)
    # localProcessGbuo = subprocess.Popen(["git", "branch", "-u", f"origin/{repo['primaryBranchName']}"], cwd=f"{localRepo['path']}",
    #                                     universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # logging.info(localProcessGbuo.stdout)
    # logging.info(
    #     f"cwd={localRepo['path']}: git branch -u origin/{repo['primaryBranchName']}")
    # if localProcessGbuo.stderr:
    #     logging.warning(localProcessGbuo.stderr)
    # localProcessGsro = subprocess.Popen(["git", "symbolic-ref", "refs/remotes/origin/HEAD",
    #                                      f"refs/remotes/origin/{repo['primaryBranchName']}"], cwd=f"{localRepo['path']}", universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # logging.info(localProcessGsro.stdout)
    # logging.info(
    #     f"cwd={localRepo['path']}: git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/{repo['primaryBranchName']}")
    # if localProcessGsro.stderr:
    #     logging.warning(localProcessGsro.stderr)
    # localPath = "/Users/gareth/Code"
    # testRepo = "test-blm"
    # testProcess = subprocess.Popen(
    #     ["git", "clone", f"https://github.com/Twitchkidd/{testRepo}.git"], cwd=localPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    # print(f"process stdout read length: {len(testProcess.stdout.read())}")
    # print(testProcess.stdout.read())
    # testStderr = testProcess.stderr.read()
    # print(f"process stderr read length: {len(testStderr)}")
    # print(testStderr)
    # config = Path.home() / ".gitconfig"
    # with config.open("r") as f:
    #     content = f.read().splitlines()
    #     for line in content:
    #         print(line)
    gitNewGcg = Popen(["git", "config", "--global", "alias.new", "'!git init && git symbolic-ref HEAD refs/heads/main'"],
                      stdout=PIPE, stderr=PIPE)
    print("git config --global alias.new '!git init && git symbolic-ref HEAD refs/heads/main'")
    gitNewGcgStdout, gitNewGcgStderr = gitNewGcg.communicate()
    if len(gitNewGcgStdout) > 0:
        print(gitNewGcgStdout)
    if len(gitNewGcgStderr) > 0:
        print(gitNewGcgStderr)
        print(f"Error creating git alias! {gitNewGcgStderr}")
        return


if __name__ == "__main__":
    main()
