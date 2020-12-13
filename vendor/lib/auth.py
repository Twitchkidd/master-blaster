from vendor.lib.reporting import getUsername
from vendor.lib.reporting import getToken
from vendor.lib.actions.network import getRepos

# auth #
# * This file should handle the process of authenticating the user,
# * including input of the username, and getting and verifying the
# * token, which should be returned second in a touple with the username,
# * and the token as None if it failed, from the auth function. * #


def auth(testing):
    """Get GitHub username, get token, validate token, return data,
    which should be a username, token, and repos."""
    username = ""
    username = getUsername(testing)

    token = ""
    token = getToken(testing)

    repos = []
    repos = getRepos(username, token)

    return username, token, repos