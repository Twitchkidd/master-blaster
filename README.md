# master-blaster

Rename primary branches of code repositories!

### v1.1!!!

Hello! Anyone coming in to contribute, I'm going to be working in the v1.1 project in the projects tab and on the 'dev' branch!

### v1!!!

Woohoo! Ready to launch this thing! It's not perfect, but it does the thing, at least on my machine! 😉

## Warnings!

This is NOT guaranteed to work!

GITHUB users!

OPERATING SYSTEM! Only tested on macOS Catalina 10.15.5

Only for repos you're the owner of, rather than collaborating on or are a member of the organization, for the moment.

The connection going down is not accounted for right now! If it's halfway through cloning repos it could leave the temporary directory on your hard drive, and potentially not work if it's not removed before the next try!

If you need to clone a lot of data over, that's a lot of data!

## However!

It's designed at least to not go ahead unless it considers conditions ideal! Asks first, too!

## What It Does!

You choose a name for your repos, authenticate, and then it will offer one of three processes for the sets of repos that fit these criteria:

If:

- The remote has a master branch,
- And not that name as a branch,
- And the default branch is master,
  And if there's a local copy of that repo:
- The local copy has a master branch,
- And no branch with the specified name,

It'll move/rename the branch and its corresponding reflog, push that to origin, change the default branch on GitHub, and then delete the master branch on origin, and if there's no local repo, it'll clone it, and clean up after if that option was selected. Default yes.

If:

- The remote has no master branch,
- And that name as a branch,
- And that name is the default branch,
- And there's a local copy with that name,
- But it also has a master branch,

It'll remove the spare master branch. Default no.

And if there was a repo that was cloned locally, and then had it's name, reflog, and default updated from another machine, it asks if it wants to update them. The criteria here are:

- The remote has no master branch,
- And that name as a branch,
- And that name is the default branch,
- And there's a local copy with just master,
- And no branch of that name.

It also optionally adds a git alias `git new` that starts up repos with 'main' or a custon name already!

## Instructions!

To run `master-blaster`, have Python 3.7 or up installed, and pipenv. Then:

`git clone https://github.com/Twitchkidd/master-blaster.git`
`cd master-blaster`
`pipenv install`
`pipenv shell`
`master-blaster`

## Thank you!
