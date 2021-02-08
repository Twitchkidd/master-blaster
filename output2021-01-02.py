# gareth@MacBook-Pro-4:~/Code/master-blaster|dev⚡ ⇒  pipenv install . && blm
# Installing .…
# Adding wcwidth to Pipfile's [packages]…
# ✔ Installation Succeeded
# Installing dependencies from Pipfile.lock (a1aa0c)…
#   🐍   ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉ 1/1 — 00:00:00

#       master-blaster: batch rename primary branches of git repos
#       and update the associated default branches on GitHub.
#       Copyright (C) 2021  Gareth Field field.gareth@gmail.com

#       This program is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
#       (at your option) any later version.

#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.

#       You should have received a copy of the GNU General Public License
#       along with this program.  If not, see <https://www.gnu.org/licenses/>.

#       ----------------------------------------------------------------------

#       Welcome to master-blaster! This program batch renames the primary
#       branches for git repos and updates the 'default' branch on GitHub.


#       Log file to be found at ./info.log!

#       Also, GitHub is deprecating password-based token generation! This is great for
#       security, it just means you're going to have to go to GitHub.com and
#       come back with an access token to run the program, and it's a couple of steps,
#       still faster than doing each manually if you have a bunch of repos, though.
#       Thank you!

# ? First, please enter your GitHub username! l
# ? Confirm username: l  Yes
# ?
#     -- Token-getting time! --

#     For good security, password-based token generation is being
#     deprecated, so these are the steps to get a personal access
#     token with the correct scope:

#     Browse to https://github.com, sign in, then go to 'Settings',
#     then 'Developer Settings', then 'Personal access tokens',
#     then 'Generate new token', confirm your password, select the
#     'repo' scope, then 'Generate Token', then copy that to clipboard.

#     To avoid repeat in case of network error, save it somewhere first,
#     then paste it back here into the prompt and hit enter to continue:

#     For thorough and visual instructions in the GitHub docs,
#     see the personal access tokens part: https://bit.ly/2X0cr3j

#      *


# Checking for repos ...
# Repos received!


#       Currently the only supported set of repos is all repos
#       user is owner of, public and private.

# ? What would you like to name your primary branches? (Default 'main'.)  All primary branc
# hes renamed to 'main'.
# ?
#       Repositories not present locally will be cloned to a temporary folder,
#       updated, the update pushed, (the default branch on GitHub.com updated,) and
#       then deleted locally depending on your choice in just a moment.

#       To potentially decrease use of bandwidth and reduce conflicts, master-blaster
#       can scan for repositories present locally, starting from the home folder or a
#       specified code directory. Yes, or everything from the cloud?
#       Yes


# ?
#       Do you keep all of your coding projects in a certain directory? Type that in
#       here to limit and speed up search. Default is home, ~/, hit enter for default.
#       Example: /Users/gareth/Code


# ?
#       Default: use '~/' for local directory search?
#       Yes


# ?
#       Remove newly cloned repositories after process complete? Defaults to yes.
#       Yes


# ?
#       Add a git alias 'git new' that initializes
#       new git repos with HEAD as main? Defaults to yes.
#       Yes


# Checking repos ...
# get_local_repos
[
    {
        "name": "deleteLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/deleteLocal",
        "gitUrl": "git://github.com/montymcblaster88/deleteLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/deleteLocal.git",
        "default": "main",
        "targetName": "main",
    },
    {
        "name": "deleteLocalAndRemote",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/deleteLocalAndRemote",
        "gitUrl": "git://github.com/montymcblaster88/deleteLocalAndRemote.git",
        "sshUrl": "git@github.com:montymcblaster88/deleteLocalAndRemote.git",
        "default": "main",
        "targetName": "main",
    },
    {
        "name": "deleteRemoteClone",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/deleteRemoteClone",
        "gitUrl": "git://github.com/montymcblaster88/deleteRemoteClone.git",
        "sshUrl": "git@github.com:montymcblaster88/deleteRemoteClone.git",
        "default": "main",
        "targetName": "main",
    },
    {
        "name": "deleteRemoteLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/deleteRemoteLocal",
        "gitUrl": "git://github.com/montymcblaster88/deleteRemoteLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/deleteRemoteLocal.git",
        "default": "main",
        "targetName": "main",
    },
    {
        "name": "localProcess",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/localProcess",
        "gitUrl": "git://github.com/montymcblaster88/localProcess.git",
        "sshUrl": "git@github.com:montymcblaster88/localProcess.git",
        "default": "main",
        "targetName": "main",
    },
    {
        "name": "mvThirdToTargetAndBlastLocalMaster",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetAndBlastLocalMaster",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetAndBlastLocalMaster.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetAndBlastLocalMaster.git",
        "default": "main",
        "targetName": "main",
    },
    {
        "name": "mvThirdToTargetAndBlastRemoteAndLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteAndLocal",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteAndLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetAndBlastRemoteAndLocal.git",
        "default": "prod",
        "targetName": "main",
    },
    {
        "name": "mvThirdToTargetAndBlastRemoteMasterClone",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteMasterClone",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteMasterClone.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetAndBlastRemoteMasterClone.git",
        "default": "prod",
        "targetName": "main",
    },
    {
        "name": "mvThirdToTargetAndBlastRemoteMasterLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteMasterLocal",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteMasterLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetAndBlastRemoteMasterLocal.git",
        "default": "prod",
        "targetName": "main",
    },
    {
        "name": "mvThirdToTargetClone",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetClone",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetClone.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetClone.git",
        "default": "main",
        "targetName": "main",
    },
    {
        "name": "mvThirdToTargetLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetLocal",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetLocal.git",
        "default": "main",
        "targetName": "main",
    },
    {
        "name": "myPrivateRepo",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/myPrivateRepo",
        "gitUrl": "git://github.com/montymcblaster88/myPrivateRepo.git",
        "sshUrl": "git@github.com:montymcblaster88/myPrivateRepo.git",
        "default": "master",
        "targetName": "main",
    },
    {
        "name": "remoteProcessClone",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/remoteProcessClone",
        "gitUrl": "git://github.com/montymcblaster88/remoteProcessClone.git",
        "sshUrl": "git@github.com:montymcblaster88/remoteProcessClone.git",
        "default": "main",
        "targetName": "main",
    },
    {
        "name": "remoteProcessLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/remoteProcessLocal",
        "gitUrl": "git://github.com/montymcblaster88/remoteProcessLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/remoteProcessLocal.git",
        "default": "main",
        "targetName": "main",
    },
]
# Checking deleteLocal ... got it!
# Checking deleteLocalAndRemote ... got it!
# Checking deleteRemoteClone ... got it!
# Checking deleteRemoteLocal ... got it!
# Checking localProcess ... got it!
# Checking mvThirdToTargetAndBlastLocalMaster ... got it!
# Checking mvThirdToTargetAndBlastRemoteAndLocal ... got it!
# Checking mvThirdToTargetAndBlastRemoteMasterClone ... got it!
# Checking mvThirdToTargetAndBlastRemoteMasterLocal ... got it!
# Checking mvThirdToTargetClone ... got it!
# Checking mvThirdToTargetLocal ... got it!
# Checking myPrivateRepo ... got it!
# Checking remoteProcessClone ... got it!
# Checking remoteProcessLocal ... got it!
# check_remote_branches
[
    {
        "name": "deleteLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/deleteLocal",
        "gitUrl": "git://github.com/montymcblaster88/deleteLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/deleteLocal.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
    {
        "name": "deleteLocalAndRemote",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/deleteLocalAndRemote",
        "gitUrl": "git://github.com/montymcblaster88/deleteLocalAndRemote.git",
        "sshUrl": "git@github.com:montymcblaster88/deleteLocalAndRemote.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
    {
        "name": "deleteRemoteClone",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/deleteRemoteClone",
        "gitUrl": "git://github.com/montymcblaster88/deleteRemoteClone.git",
        "sshUrl": "git@github.com:montymcblaster88/deleteRemoteClone.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
    {
        "name": "deleteRemoteLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/deleteRemoteLocal",
        "gitUrl": "git://github.com/montymcblaster88/deleteRemoteLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/deleteRemoteLocal.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
    {
        "name": "localProcess",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/localProcess",
        "gitUrl": "git://github.com/montymcblaster88/localProcess.git",
        "sshUrl": "git@github.com:montymcblaster88/localProcess.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
    {
        "name": "mvThirdToTargetAndBlastLocalMaster",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetAndBlastLocalMaster",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetAndBlastLocalMaster.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetAndBlastLocalMaster.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
    {
        "name": "mvThirdToTargetAndBlastRemoteAndLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteAndLocal",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteAndLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetAndBlastRemoteAndLocal.git",
        "default": "prod",
        "targetName": "main",
        "hasTarget": False,
        "hasMaster": True,
    },
    {
        "name": "mvThirdToTargetAndBlastRemoteMasterClone",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteMasterClone",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteMasterClone.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetAndBlastRemoteMasterClone.git",
        "default": "prod",
        "targetName": "main",
        "hasTarget": False,
        "hasMaster": True,
    },
    {
        "name": "mvThirdToTargetAndBlastRemoteMasterLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteMasterLocal",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteMasterLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetAndBlastRemoteMasterLocal.git",
        "default": "prod",
        "targetName": "main",
        "hasTarget": False,
        "hasMaster": True,
    },
    {
        "name": "mvThirdToTargetClone",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetClone",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetClone.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetClone.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
    {
        "name": "mvThirdToTargetLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetLocal",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetLocal.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
    {
        "name": "myPrivateRepo",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/myPrivateRepo",
        "gitUrl": "git://github.com/montymcblaster88/myPrivateRepo.git",
        "sshUrl": "git@github.com:montymcblaster88/myPrivateRepo.git",
        "default": "master",
        "targetName": "main",
        "hasTarget": True,
        "hasMaster": True,
    },
    {
        "name": "remoteProcessClone",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/remoteProcessClone",
        "gitUrl": "git://github.com/montymcblaster88/remoteProcessClone.git",
        "sshUrl": "git@github.com:montymcblaster88/remoteProcessClone.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
    {
        "name": "remoteProcessLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/remoteProcessLocal",
        "gitUrl": "git://github.com/montymcblaster88/remoteProcessLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/remoteProcessLocal.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
]
# check_branches
[
    {
        "name": "deleteLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/deleteLocal",
        "gitUrl": "git://github.com/montymcblaster88/deleteLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/deleteLocal.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
    {
        "name": "deleteLocalAndRemote",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/deleteLocalAndRemote",
        "gitUrl": "git://github.com/montymcblaster88/deleteLocalAndRemote.git",
        "sshUrl": "git@github.com:montymcblaster88/deleteLocalAndRemote.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
    {
        "name": "deleteRemoteClone",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/deleteRemoteClone",
        "gitUrl": "git://github.com/montymcblaster88/deleteRemoteClone.git",
        "sshUrl": "git@github.com:montymcblaster88/deleteRemoteClone.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
    {
        "name": "deleteRemoteLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/deleteRemoteLocal",
        "gitUrl": "git://github.com/montymcblaster88/deleteRemoteLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/deleteRemoteLocal.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
    {
        "name": "localProcess",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/localProcess",
        "gitUrl": "git://github.com/montymcblaster88/localProcess.git",
        "sshUrl": "git@github.com:montymcblaster88/localProcess.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
    {
        "name": "mvThirdToTargetAndBlastLocalMaster",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetAndBlastLocalMaster",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetAndBlastLocalMaster.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetAndBlastLocalMaster.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
    {
        "name": "mvThirdToTargetAndBlastRemoteAndLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteAndLocal",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteAndLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetAndBlastRemoteAndLocal.git",
        "default": "prod",
        "targetName": "main",
        "hasTarget": False,
        "hasMaster": True,
    },
    {
        "name": "mvThirdToTargetAndBlastRemoteMasterClone",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteMasterClone",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteMasterClone.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetAndBlastRemoteMasterClone.git",
        "default": "prod",
        "targetName": "main",
        "hasTarget": False,
        "hasMaster": True,
    },
    {
        "name": "mvThirdToTargetAndBlastRemoteMasterLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteMasterLocal",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteMasterLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetAndBlastRemoteMasterLocal.git",
        "default": "prod",
        "targetName": "main",
        "hasTarget": False,
        "hasMaster": True,
    },
    {
        "name": "mvThirdToTargetClone",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetClone",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetClone.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetClone.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
    {
        "name": "mvThirdToTargetLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetLocal",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetLocal.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
    {
        "name": "myPrivateRepo",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/myPrivateRepo",
        "gitUrl": "git://github.com/montymcblaster88/myPrivateRepo.git",
        "sshUrl": "git@github.com:montymcblaster88/myPrivateRepo.git",
        "default": "master",
        "targetName": "main",
        "hasTarget": True,
        "hasMaster": True,
    },
    {
        "name": "remoteProcessClone",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/remoteProcessClone",
        "gitUrl": "git://github.com/montymcblaster88/remoteProcessClone.git",
        "sshUrl": "git@github.com:montymcblaster88/remoteProcessClone.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
    {
        "name": "remoteProcessLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/remoteProcessLocal",
        "gitUrl": "git://github.com/montymcblaster88/remoteProcessLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/remoteProcessLocal.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
    },
]
# check_names
[
    {
        "name": "deleteLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/deleteLocal",
        "gitUrl": "git://github.com/montymcblaster88/deleteLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/deleteLocal.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
        "status": ["Already blasted."],
    },
    {
        "name": "deleteLocalAndRemote",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/deleteLocalAndRemote",
        "gitUrl": "git://github.com/montymcblaster88/deleteLocalAndRemote.git",
        "sshUrl": "git@github.com:montymcblaster88/deleteLocalAndRemote.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
        "status": ["Already blasted."],
    },
    {
        "name": "deleteRemoteClone",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/deleteRemoteClone",
        "gitUrl": "git://github.com/montymcblaster88/deleteRemoteClone.git",
        "sshUrl": "git@github.com:montymcblaster88/deleteRemoteClone.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
        "status": ["Already blasted."],
    },
    {
        "name": "deleteRemoteLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/deleteRemoteLocal",
        "gitUrl": "git://github.com/montymcblaster88/deleteRemoteLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/deleteRemoteLocal.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
        "status": ["Already blasted."],
    },
    {
        "name": "localProcess",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/localProcess",
        "gitUrl": "git://github.com/montymcblaster88/localProcess.git",
        "sshUrl": "git@github.com:montymcblaster88/localProcess.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
        "status": ["Already blasted."],
    },
    {
        "name": "mvThirdToTargetAndBlastLocalMaster",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetAndBlastLocalMaster",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetAndBlastLocalMaster.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetAndBlastLocalMaster.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
        "status": ["Already blasted."],
    },
    {
        "name": "mvThirdToTargetAndBlastRemoteAndLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteAndLocal",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteAndLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetAndBlastRemoteAndLocal.git",
        "default": "prod",
        "targetName": "main",
        "hasTarget": False,
        "hasMaster": True,
        "status": ["Path unclear."],
    },
    {
        "name": "mvThirdToTargetAndBlastRemoteMasterClone",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteMasterClone",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteMasterClone.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetAndBlastRemoteMasterClone.git",
        "default": "prod",
        "targetName": "main",
        "hasTarget": False,
        "hasMaster": True,
        "status": ["Path unclear."],
    },
    {
        "name": "mvThirdToTargetAndBlastRemoteMasterLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteMasterLocal",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetAndBlastRemoteMasterLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetAndBlastRemoteMasterLocal.git",
        "default": "prod",
        "targetName": "main",
        "hasTarget": False,
        "hasMaster": True,
        "status": ["Path unclear."],
    },
    {
        "name": "mvThirdToTargetClone",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetClone",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetClone.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetClone.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
        "status": ["Already blasted."],
    },
    {
        "name": "mvThirdToTargetLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/mvThirdToTargetLocal",
        "gitUrl": "git://github.com/montymcblaster88/mvThirdToTargetLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/mvThirdToTargetLocal.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
        "status": ["Already blasted."],
    },
    {
        "name": "myPrivateRepo",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/myPrivateRepo",
        "gitUrl": "git://github.com/montymcblaster88/myPrivateRepo.git",
        "sshUrl": "git@github.com:montymcblaster88/myPrivateRepo.git",
        "default": "master",
        "targetName": "main",
        "hasTarget": True,
        "hasMaster": True,
        "status": ["Path unclear."],
    },
    {
        "name": "remoteProcessClone",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/remoteProcessClone",
        "gitUrl": "git://github.com/montymcblaster88/remoteProcessClone.git",
        "sshUrl": "git@github.com:montymcblaster88/remoteProcessClone.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
        "status": ["Already blasted."],
    },
    {
        "name": "remoteProcessLocal",
        "ownerLogin": "montymcblaster88",
        "htmlUrl": "https://github.com/montymcblaster88/remoteProcessLocal",
        "gitUrl": "git://github.com/montymcblaster88/remoteProcessLocal.git",
        "sshUrl": "git@github.com:montymcblaster88/remoteProcessLocal.git",
        "default": "main",
        "targetName": "main",
        "hasMaster": False,
        "hasTarget": True,
        "status": ["Already blasted."],
    },
]

# Process complete!

# 10 repos were already blasted!

# Repos: 10
# deleteLocal
# deleteLocalAndRemote
# deleteRemoteClone
# deleteRemoteLocal
# localProcess
# mvThirdToTargetAndBlastLocalMaster
# mvThirdToTargetClone
# mvThirdToTargetLocal
# remoteProcessClone
# remoteProcessLocal


# 4 repos weren't acted on because the path for action was unclear!

# Repos: 4
# mvThirdToTargetAndBlastRemoteAndLocal
# mvThirdToTargetAndBlastRemoteMasterClone
# mvThirdToTargetAndBlastRemoteMasterLocal
# myPrivateRepo


# Git alias `git new` set (or re-set.)

# Check the log file at ./info.log for details.

# Thank you for using master-blaster!