def sayHi():
    print("Hello!")


# * ~~~ Set of questionary dictionary questions! ~~~ * #

# * ``` Placeholder variable for repo types!``` * #
repoTypes = ""

# * ``` What types of repos! ``` * #

# * ``` Question ``` * #
repoTypesPrompt = """
    What set of repositories do you want to update?
"""

# * ``` Choices ``` * #
repoTypesOwner = "All repositories I'm the owner of, public and private. (Collaborator/Organization repo types in development!)"
repoTypesOwnerPublic = "All repositories I'm the owner of, only public, not private."
repoTypesAll = "All repositories I'm the owner, collaborator, and/or organization member, public and private."
repoTypesAllPublic = "All repositories I'm the owner, collaborator, and/or organization member, only public, not private."
repoTypesCollaborator = (
    "All repositories I'm the owner of and/or a collaborator on, public and private."
)
repoTypesCollaboratorPublic = "All repositories I'm the owner of and/or a collaborator on, only public, not private."
repoTypesOrganization = "All repositories I'm the owner of and/or a member of the organization, public and private."
repoTypesOrganizationPublic = "All repositories I'm the owner of and/or a member of the organization, only public, not private."

# * ``` What to name the primary branches and choices! ``` * #

# * ``` Question ``` * #
namesSelectionPrompt = """
    What would you like to name your primary branches? (Default 'main'.)
"""

# * ``` Choices ``` * #
namesMain = "All primary branches renamed to 'main'."
namesCustom = "Choose name for all primary branches renamed to. "
namesPerRepo = "Choose a name for the primary branch for each repo."

questions = [
    {
        "type": "select",
        "name": "repoTypes",
        "message": repoTypesPrompt,
        "choices": [
            repoTypesOwner,
            # repoTypesOwnerPublic,
            # repoTypesAll,
            # repoTypesAllPublic,
            # repoTypesCollaborator,
            # repoTypesCollaboratorPublic,
            # repoTypesOrganization,
            # repoTypesOrganizationPublic
        ],
    },
    {
        "type": "select",
        "name": "namesSelection",
        "message": namesSelectionPrompt,
        "choices": [namesMain, namesCustom, namesPerRepo],
    },
]

# * ``` Extract the data from the set of prompts from dictionary! ``` * #
answers = questionary.prompt(questions)
# repoTypes = answers['repoTypes']
repoTypes = "All repositories I'm the owner of, public and private."
logging.info(f"Repository types chosen: {repoTypes}")
logging.info(f"Naming selection: {answers['namesSelection']}")

# * ~~~ Custom primary branch flow! ~~~ * #

# * ``` Placeholder variable for the primary branch name! ``` * #
name = "main"

# * ``` Custom name for all branches! ``` * #
customNamePrompt = """
    What name are you choosing for primary branches?
"""

# * ``` Confirm reset to main! ``` * #
confirmResetToMainPrompt = """
    Default: use 'main' for all primary branches?
"""


def customNameConfirmPrompt(inputName):
    return f"""{inputName} for all primary branches?"""


if answers["namesSelection"] == namesCustom:
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
                logging.info(f"Name for primary branches: {name}")
            else:
                continue
        else:
            confirmCustomNameResponse = questionary.confirm(
                customNameConfirmPrompt(customNameResponse)
            ).ask()
            if confirmCustomNameResponse:
                name = customNameResponse
                nameConfirmed = True
                logging.info(f"Name for primary branches: {name}")
                pass

# * ~~~ Interactive naming mode choice handling! ~~~ * #

# * ``` Placeholder variable for interactive naming mode! ``` * #
interactive = False

# * ``` Confirmation that interactive naming mode will happen! ``` * #
interactiveNamingConfirmationPrompt = """
    Okay! We'll name them after we fetch the set of repos!
"""

if answers["namesSelection"] == namesPerRepo:
    interactive = True
    print(interactiveNamingConfirmationPrompt)

# * ~~~ Local directory choice handling! ~~~ * #

# * ``` Local directory yay or nay! ``` * #
localDirectoriesPrompt = """
    Repositories not present locally will be cloned to a temporary folder,
    updated, the update pushed, (the default branch on GitHub.com updated,) and
    then deleted locally depending on your choice in just a moment.
    
    The program can decrease the use of bandwidth and reduce potential conflicts
    by scanning for repositories that are present locally, from home or a specified
    directory for code. Okay?
"""
localDirectories = questionary.confirm(localDirectoriesPrompt).ask()

# * ``` Placeholder variable for local directory selection! ``` * #
localDirectory = Path.home()

# * ``` Which local directory? ``` * #
localDirectoryPrompt = """
    Do you keep all of your coding projects in a certain directory? Type that in
    here to limit and speed up search. Default is home, ~/, hit enter for default.
    Example: /Users/gareth/Code
"""

# * ``` Confirm reset to home! ``` * #
confirmResetToHomePrompt = """
    Default: use '~/' for local directory search?
"""

# * ``` Placeholder variable for confirming removal of local directories after! ``` * #
confirmRemoveLocalDirectoriesAfter = False


def customLocalDirectoryConfirmPrompt(inputDir):
    return f"""{inputDir} for all primary branches?"""


# * ``` Ask which directory to use to search for local repos! ``` * #
if localDirectories:
    localDirectoryConfirmed = False
    while not localDirectoryConfirmed:
        customLocalDirectoryResponse = questionary.text(localDirectoryPrompt).ask()
        if customLocalDirectoryResponse == "":
            confirmResetToHomeResponse = questionary.confirm(
                confirmResetToHomePrompt
            ).ask()
            if confirmResetToHomeResponse:
                localDirectory = Path.home()
                localDirectoryConfirmed = True
                # ! Testing ! #
                # logging.info(f"Local directory to search: {localDirectory}")
            else:
                continue
        else:
            if os.path.isdir(customLocalDirectoryResponse):
                confirmCustomLocalDirectoryResponse = questionary.confirm(
                    customLocalDirectoryConfirmPrompt(customLocalDirectoryResponse)
                ).ask()
                if confirmCustomLocalDirectoryResponse:
                    localDirectory = customLocalDirectoryResponse
                    localDirectoryConfirmed = True
                    # ! Testing! #
                    # logging.info(
                    #     f"Local directory to search: {localDirectory}")
                    pass
            else:
                print(
                    f"Error! Directory not showing as valid: {customLocalDirectoryResponse}"
                )
                continue

# ! Testing! #
localDirectory = f"{Path.home()}/Code"
logging.info(f"Local directory to search: {localDirectory}")

# * ``` Ask to delete cloned repos! ``` * #
confirmRemoveLocalDirectoriesAfterPrompt = """
    Remove newly cloned repositories after process complete? Defaults to yes.
"""

if localDirectories:
    confirmRemoveLocalDirectoriesAfter = questionary.confirm(
        confirmRemoveLocalDirectoriesAfterPrompt
    ).ask()
    # ! Testing! #
    # logging.info(
    #     f"Confirm remove local directories after: {confirmRemoveLocalDirectoriesAfter}")

# ! Testing! #
confirmRemoveLocalDirectoriesAfter = True
logging.info(
    f"Confirm remove local directories after: {confirmRemoveLocalDirectoriesAfter}"
)

# * ~~~ New Git Alias! ~~~ * #

# * ``` Placeholder variable for git alias selection! ``` * #
gitNew = True

# * ``` Prompt! ``` * #
gitNewPrompt = f"""
    Add a git alias 'git new' that initializes
    new git repos with commit as {name}? Defaults to yes.
"""

# * ``` Ask it! ``` * #
if not interactive:
    gitNew = questionary.confirm(gitNewPrompt)
    # * ``` Log the choice! ``` * #
    logging.info(f"Add git alias `git new`: {name}")
