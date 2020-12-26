import logging, sys
from vendor.lib.reporting import get_username, get_token
from vendor.lib.actions.network import get_repos
from vendor.lib.actions.network_exceptions import NetworkConnectivityError
from vendor.lib.actions.network_exceptions import RequestError
from vendor.lib.actions.network_exceptions import NoReposError


def auth(testing):
    """Get GitHub username, get token, validate token, return data,
    which should be a username, token, and repos."""
    try:
        username = get_username(testing)
        token = get_token(testing)
        repos = get_repos(username, token)
        return username, token, repos
    except NetworkConnectivityError as err:
        logging.warning(err)
        print(err.message)
        sys.exit(1)
    except RequestError as err:
        logging.warning(err)
        print(
            f"Network error! Is {username} your username? Maybe the token? Please try again!"
        )
        sys.exit(1)
    except NoReposError as err:
        logging.warning(err)
        print(err.message)
        sys.exit(1)
