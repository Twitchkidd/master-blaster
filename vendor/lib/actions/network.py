

# networkActions #
# * Actions taken over the network. * #

Declare the GitHub API url


def getReposUrl():
    url = f"{GITHUB_API}/user/repos"
    return url

# * ``` Construct the headers! ``` * #


def getReposHeaders(token):
    headers = {"Authorization": 'token ' + token}
    return headers

# * ``` Custruct the parameters! ``` * #


def getReposParams():
    params = {"per_page": "1000", "type": "owner"}
    return params


def getRepos():
    """Initial get of repo names"""


def getBranchUrl(repo, branch):


# * ``` Constructing the url! ``` * #


def constructReposUrl():
    return f"{GITHUB_API}/user/repos"


# * ``` Construct the headers! ``` * #


def constructHeaders(token):
    headers = {"Authorization": "token " + token}
    return headers


# * ``` Custruct the parameters! ``` * #


def constructReposParams():
    params = {}
    if repoTypes == repoTypesAll:
        params = {
            "per_page": "1000",
        }
    if repoTypes == repoTypesAllPublic:
        params = {"per_page": "1000", "visibility": "public"}
    # if repoTypes == repoTypesOwner:
    if repoTypes == "All repositories I'm the owner of, public and private.":
        params = {"per_page": "1000", "type": "owner"}
    if repoTypes == repoTypesOwnerPublic:
        params = {"per_page": "1000", "visibility": "public", "type": "owner"}
    if repoTypes == repoTypesCollaborator:
        params = {"per_page": "1000", "type": "owner,collaborator"}
    if repoTypes == repoTypesCollaboratorPublic:
        params = {
            "per_page": "1000",
            "visibility": "public",
            "type": "owner,collaborator",
        }
    if repoTypes == repoTypesOrganization:
        params = {"per_page": "1000", "type": "owner,collaborator,organization_member"}
    if repoTypes == repoTypesOrganizationPublic:
        params = {
            "per_page": "1000",
            "visibility": "public",
            "type": "owner,collaborator,organization_member",
        }
    return params
