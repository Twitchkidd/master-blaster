### v1.0.6 Run commands!

Ahh! Almost there, at the moment we're just going to have to be okay with the extra `pip install questionary requests`, it's just two packages, no prob.

### v1.0.5 Knock-on-wood Stable!

Bugs squashed! Still no warranty, and the testing could be more robust, and more automated, and the logging needs a brush up to be a little more helpful, but I've dog-fooded this on all 76 of my repos, and I would totally tell my friends to run this, which I think is the real test, lol. Oh, unless they're on Windows, not because of the file system, that should be fine, just I'm not sure the addition of the interpreter string at the top will play nice with winpty yet, so that's TBD for 1.0.6 at the moment.

Still looking for contributions! At the time of the writing of this README, the Projects tab hasn't been updated, but looking there and opening issues would be appreciated for sure!

Also this is packaged on PyPi now! And running it is just `pip install master-blaster` and `master-blaster`, none of that other nonsense with `pipenv`. Major improvement, lol. That's still part of development though, I should document what it takes to run the dev branch, let's see ... CONTRIBUTING.md started!

## Warnings!

This is NOT guaranteed to work!

GitHub users specifically!

HOLD THE PHONE ON THE LINE BELOW! Working on Windows 7!
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

### \*nix!

To run `master-blaster`, have Python 3.6 or up installed, and pip, then:

`pip install master-blaster`

Then, unless you have them installed already:

`pip install questionary requests`

And then run:

`master-blaster`

to start the program!

### Windows!

#### Hey, I'm sorry, I may have broken this! 1.0.7, promise!

Just instead of `master-blaster`, run `winpty python ./bin/master-blaster`!

## Thank you!
