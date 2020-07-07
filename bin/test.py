#!/usr/bin/env python

import subprocess
import requests
import json

# ! ``` Placeholder variables for the testing tokens! ``` ! #
# ! Testing! #
tokenRepoScope = ""

# ! Testing! #
with open("./repo.txt", 'r') as repoF:
    tokenRepoScope = repoF.read(40)


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
    headers = {"Authorization": 'token ' + tokenRepoScope}
    params = json.dumps({"default_branch": "main"})
    response = requests.patch("https://api.github.com/repos/Twitchkidd/master-blaster",
                              data=params, headers=headers)
    print(response.json())


if __name__ == "__main__":
    main()
