import sys
from vendor.lib.reporting import getUsername
from vendor.lib.reporting import getToken
from vendor.lib.actions.network import getRepos
from vendor.lib.logging import logWarning
from vendor.lib.actions.network import RequestError


# auth #
# * Handles authenticating the user with a username and token,
# * and verifying.


def auth(testing):
    """Get GitHub username, get token, validate token, return data,
    which should be a username, token, and repos."""

    username = getUsername(testing)
    token = getToken(testing)

    if testing:
        repos = getRepos("Herp", "derp")

    # try:
    #     if testing:
    #         repos = getRepos("Herp", "derp")
    #     repos = getRepos(username, token)
    #     return username, token, repos
    # except RequestError as err:
    #     logWarning(err)
    #     print("Network error! Try again please!")
    #     sys.exit(1)
