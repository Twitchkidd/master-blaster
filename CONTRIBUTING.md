# Contributing to `master-blaster`

TODO Tidy this up!

### v1.1.0 Changes!!

Adding tests!

`pip install -U pytest`

and then `pytest`!

---

### Previous CONTRIBUTING

Hi! Let me start this off by at least having the steps for how to run `dev`!

The first thing is if you're in ~/Code/master-blaster, it captures the current branch, because for some reason I was getting put on the main branch when I didn't mean to be. I might have fixed this, but it puts you back right at the end of the program.

Also, info.log rewrites itself each time, so that the end user has a complete log of everything `master-blaster` has done, but when developing it you just see the last test.

Then, so currently it's hardcoded so that as long as there's an input for username, the username becomes _my_ username, Twitchkidd. Replace that with your username so you don't have to type it in every time. Also, as long as there's an input for which directory to use for local search, it hardcodes to ~/Code. Similarly, that the repos cloned in should be deleted at the end of the program is hardcoded true.

The tokens are sort of hardcoded in. Put personal access tokens with the 'repo' scope and 'repo public repo' scope in repo.txt and repoPublicRepo.txt and it will read those in, as long as there's an input for the token question.

Then so working with a cloned/forked repo, you need pipenv installed, and then you run (from the project folder):

`pipenv shell`

`pipenv install .`

`master-blaster` (or, I think, `winpty master-blaster` on Windows, but I need to test this for 1.0.6)

Thank you!
