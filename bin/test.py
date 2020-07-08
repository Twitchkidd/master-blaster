#!/usr/bin/env python

import subprocess
# import requests
# import json

# # ! ``` Placeholder variables for the testing tokens! ``` ! #
# # ! Testing! #
# tokenRepoScope = ""

# # ! Testing! #
# with open("./repo.txt", 'r') as repoF:
#     tokenRepoScope = repoF.read(40)


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
    processOne = subprocess.Popen(
        ["mkdir", "-pv", "/Users/gareth/Code/master-blaster-Twitchkidd/"], cwd="/Users/gareth/Code", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutOne, stderrOne = processOne.communicate()
    print(f"stdoutOne: {stdoutOne}")
    print(f"stderrOne: {stderrOne}")
    processTwo = subprocess.Popen(
        ["git", "clone", "https://github.com/Twitchkidd/dep-server.git", "./dep-server/"], cwd="/Users/gareth/Code/master-blaster-Twitchkidd/", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutTwo, stderrTwo = processTwo.communicate()
    print(f"stdoutTwo: {stdoutTwo}")
    print(f"stderrTwo: {stderrTwo}")
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
    processSix = subprocess.Popen(
        ["git", "push", "origin", "--delete", "master"], cwd="/Users/gareth/Code/master-blaster-Twitchkidd/dep-server/", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutSix, stderrSix = processSix.communicate()
    print(f"stdoutSix: {stdoutSix}")
    print(f"stderrSix: {stderrSix}")
    processFive = subprocess.Popen(
        ["rm", "-dfRv", "/Users/gareth/Code/master-blaster-Twitchkidd/master-blaster-Twitchkidd/"], cwd="/Users/gareth/Code/", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutFive, stderrFive = processFive.communicate()
    print(f"stdoutFive: {stdoutFive}")
    print(f"stderrFive: {stderrFive}")


if __name__ == "__main__":
    main()
