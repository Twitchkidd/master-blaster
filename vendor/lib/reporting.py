import questionary
from vendor.lib.logging import logInfo
from vendor.lib.actions.shell import getLocalToken

# reporting #
# * Text! * #


def intro():
    """Print the license, intro blurb, and token blurb!"""
    licenseText = """
      master-blaster: Rename primary branches of code repositories.
      Copyright (C) 2020  Gareth Field field.gareth@gmail.com

      This program is free software: you can redistribute it and/or modify
      it under the terms of the GNU General Public License as published by
      the Free Software Foundation, either version 3 of the License, or
      (at your option) any later version.

      This program is distributed in the hope that it will be useful,
      but WITHOUT ANY WARRANTY; without even the implied warranty of
      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
      GNU General Public License for more details.

      You should have received a copy of the GNU General Public License
      along with this program.  If not, see <https://www.gnu.org/licenses/>.
  """
    print(licenseText)

    introText = """
      Welcome to master-blaster! This program batch renames primary branches
      for GitHub users! We'll go through the options before making any changes!
  """
    print(introText)

    tokenExplanation = """
      Also, GitHub is deprecating password-based token generation! This is great for
      security, it just means you're going to have to go to GitHub.com and
      come back with an access token to run the program, and it's a couple of steps,
      still faster than doing each manually if you have a bunch of repos, though.
      Thank you!
  """
    print(tokenExplanation)


def usernameConfirmationPrompt(usernameInput):
    return f"Confirm username: {usernameInput}"


def getUsername(testing):
    """Get the GitHub username and return it."""
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
                if not testing:
                    logInfo(f"Username: {username}")
                    usernameConfirmed = True
                    continue

    if testing:
        username = "Twitchkidd"
        logInfo(f"Username: {username}")

    return username


def getToken(testing):
    """Get token from user, validate, return tuple of token and repos."""
    # * Placeholder for token. * #
    token = ""

    tokenPrompt = """
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
    print(tokenPrompt)

    tokenConfirmed = False
    while not tokenConfirmed:
        customTokenResponse = questionary.text(tokenPrompt).ask()
        if customTokenResponse == "":
            print("Please enter the token!")
            continue
        else:
            token = customTokenResponse
            tokenConfirmed = True
            continue

    if testing:
        token = getLocalToken()

    return token


def repoTypesBlurb():
    """Explain all repos, owner, public/private."""
    print(
        "Currently the only supported set of repos is all repos user is owner of, public and private."
    )


def getNamingMode(main, custom, perRepo):
    return questionary.select(
        "What would you like to name your primary branches? (Default 'main'.)",
        choices=[main, custom, perRepo],
    ).ask()


def customNameConfirmPrompt(inputName):
    return f"""{inputName} for all primary branches?"""


def getCustomName():
    """For when the user wants to set all repos primary branches to a custom name."""
    # * ``` Custom name for all branches! ``` * #
    customNamePrompt = """
      What name are you choosing for primary branches?
  """
    # * ``` Confirm reset to main! ``` * #
    confirmResetToMainPrompt = """
      Default: use 'main' for all primary branches?
  """
    name = "main"
    nameConfirmed = False
    while not nameConfirmed:
        customNameResponse = questionary.text(customNamePrompt).ask()
        if customNameResponse == "":
            confirmResetToMainResponse = questionary.confirm(
                confirmResetToMainPrompt
            ).ask()
            if confirmResetToMainResponse:
                name = "main"
                nameConfirmed = True
        else:
            confirmCustomNameResponse = questionary.confirm(
                customNameConfirmPrompt(customNameResponse)
            ).ask()
            if confirmCustomNameResponse:
                name = customNameResponse
                nameConfirmed = True
    logInfo(f"Name for primary branches: {name}")
    return name


def getCustomNames(repos):
    """For when the user wants to set a custom name for each repo primary branch."""
    print(
        """
        Interactive naming mode!
    """
    )
    name = "main"
    for repo in repos:
        primaryBranchNameConfirmed = False
        while not primaryBranchNameConfirmed:
            repoNameResponse = questionary.text(
                f"Primary branch name for {repo['htmlUrl']}?"
            ).ask()
            if repoNameResponse == "":
                defaultNameResponse = questionary.confirm(
                    f"Default primary branch name {name} for {repo['htmlUrl']}?"
                )
                if defaultNameResponse:
                    repo["primaryBranchName"] = name
                    logInfo(f"Primary branch name for {repo['htmlUrl']}: {name}")
                    primaryBranchNameConfirmed = True
            else:
                customRepoNameConfirmed = questionary.confirm(
                    f"{repoNameResponse} for {repo['htmlUrl']}?"
                )
                if customRepoNameConfirmed:
                    repo["primaryBranchName"] = repoNameResponse
                    logInfo(
                        f"Primary branch name for {repo['htmlUrl']}: {repoNameResponse}"
                    )
                    primaryBranchNameConfirmed = True
    return repos


def denoument():
    print("Thank you for using master-blaster!\n")
    print("Check the log file at ./info.log for details!")
