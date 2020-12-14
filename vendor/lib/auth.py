import sys
from vendor.lib.reporting import getUsername
from vendor.lib.reporting import getToken
from vendor.lib.actions.network import getRepos
from vendor.lib.logging import logWarning
from vendor.lib.actions.network import NetworkError
from vendor.lib.actions.network import RequestError
from vendor.lib.actions.network import NoReposError


# auth #
# * Handles authenticating the user with a username and token,
# * and verifying.


def auth(testing):
    """Get GitHub username, get token, validate token, return data,
    which should be a username, token, and repos."""

    username = getUsername(testing)
    token = getToken(testing)

    try:
        if testing:
            repos = getRepos("Herp", "derp")
        repos = getRepos(username, token)
        return username, token, repos
    except NetworkError as err:
        logWarning(err)
        print(err.message)
        sys.exit(1)
    except RequestError as err:
        logWarning(err)
        print(
            f"Network error! Is {username} your username? Maybe the token? Please try again!"
        )
        sys.exit(1)
    except NoReposError as err:
        logWarning(err)
        print(err.message)
        sys.exit(1)
