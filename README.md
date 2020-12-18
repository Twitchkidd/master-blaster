# master-blaster

Rename primary branches of code repositories!

### v1.1.0 Fall Reboot!

First thing is to update to Python 3.8 in the Pipfile and recoil in horror that you can't specify version ranges in a Pipfile, just whaaaaaaat

I removed this:

requests = "\*"
questionary = "\*"

from [packages]!

`questionary` and `requests` are now embedded in the project! Much easier!

Just `pip install master-blaster && master-blaster` !
