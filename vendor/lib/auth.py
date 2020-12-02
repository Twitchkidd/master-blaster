

# auth #
# * This file should handle the process of authenticating the user,
# * including input of the username, and getting and verifying the
# * token, which should be returned second in a touple with the username,
# * and the token as None if it failed, from the auth function. * #

def auth(testing):
    """Get GitHub username, get token, validate token, return data,
    which should be a username, token, and repos."""
    # shellActions #
    If testing, grab the current branch.
    # reporting #
    Explain the gist of the token thing.

    Placeholder for username.

    Username prompt.

    Confirm username.
    # logging #
    Log username.

    Placeholder for token.

    If testing:
        # shellActions #
    Grab locally stored token.
    # reporting #
    Prompt for token.

    Confirm token.

    Placeholder for repos.

    # networkActions #
    Get list of repos, validating token.

    Or break the program.

    # logging #
    And log it.

    Otherwise, scrub data, populate repos.

    return (username, token, repos)


import logging
import os
import sys

# * This file should handle the process of authenticating the user,
# * including input of the username, and getting and verifying the
# * token, which should be returned second in a touple with the username,
# * and the token as None if it failed, from the auth function. * #

# what if you appended with Path, like
# sys.path.append(Path.cwd() / "vendor")

# Add vendor directory to module search path
parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, "vendor")

sys.path.append(vendor_dir)

import questionary
import requests

# Plz return None if auth fails!


def usernameConfirmationPrompt(usernameInput):
    return f"Confirm username: {usernameInput}"


def tokenPrompt():
    return f"""
    -- Token-getting time! --

    For good security, password-based token generation is being
    deprecated, so these are the steps to get a personal access
    token with the correct scope:

    Browse to https://github.com, sign in, then go to 'Settings',
    then 'Developer Settings', then 'Personal access tokens',
    then 'Generate new token', confirm your password, select the
    'repo' scope, then 'Generate Token', then copy that to clipboard.

    To avoid repeat in case of network error, save it somewhere first,
    then paste it back here into the prompt and hit enter to continue:

    For thorough and visual instructions in the GitHub docs,
    see the personal access tokens part: https://bit.ly/2X0cr3j
    
    """


def getToken(testing):
    tokenConfirmed = False
    while not tokenConfirmed:
        customTokenResponse = questionary.text(tokenPrompt("repo")).ask()
        if customTokenResponse == "":
            print("Please enter the token!")
            continue
        else:
            token = customTokenResponse
            tokenConfirmed = True
            continue
    if testing:
        # ! Testing! #
        token = tokenRepoScope
        # # token = "fermf"
    return token


def auth(testing):
    # * ~~~  Username gathering! ~~~ * #
    # * ``` Placeholder variable for the username! ``` * #
    username = ""

    # * ``` Ask for username! ``` * #
    usernamePrompt = """
      First, please enter your GitHub username!
    """

    usernameConfirmed = False
    while not usernameConfirmed:
        usernameResponse = questionary.text(usernamePrompt).ask()
        if usernameResponse == "":
            print("GitHub username blank: Please try again!")
            continue
        if len(usernameResponse) >= 40:
            print("GitHub usernames are 39 chars or less: please try again!")
            continue
        else:
            usernameConfirmationResponse = questionary.confirm(
                usernameConfirmationPrompt(usernameResponse)
            ).ask()
            if usernameConfirmationResponse == False:
                print("Thank you for retrying!")
                continue
            if usernameConfirmationResponse:
                username = usernameResponse
                # ! Testing! #
                # logging.info(f"Username: {username}")
                usernameConfirmed = True
                continue

    # * ``` Placeholder variables for the token! ``` * #
    token = ""

    # ! Testing ! #
    if testing:
        username = "Twitchkidd"
        logging.info(f"Username: {username}")

    # ! Testing! #
    # * ``` Placeholder variables for the testing tokens! ``` * #
    tokenRepoScope = ""

    # ! Testing! #
    with open("./repo.txt", "r") as repoF:
        tokenRepoScope = repoF.read(40)
