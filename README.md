# master-blaster

Batch rename primary branches of git repos and update the associated default branches on GitHub!

[![Excalidraw chart](https://raw.githubusercontent.com/Twitchkidd/master-blaster/dev/master-blaster-excalidraw-1x.png)](https://raw.githubusercontent.com/Twitchkidd/master-blaster/dev/master-blaster-excalidraw-3x.png 'Excalidraw chart, high res')

### v1.1.0 Reboot 2021!

#### Update Feb 2nd:

I got totally distracted by trying to make a Pac-Man clone in the browser running on NextJs and connecting to MongoDb! ADD strikes again, it's not so much that I _can't_ focus, I'm just not always in control of what I focus _on._ I think I may be about to get an internship working on an integration for a start-up, so I'll be replanning my dev time very soon, so this project can get some love.

If I remember correctly, I needed to abstract out the procedures in /vendor/lib/dispatch.py because I had written functions for each case (do _this_ and _that_ and _that_ would be doThisThatThat(): ...) and make them (and their error handling) composable.

Also, I have **no** idea how I'd go about testing this, and it obviously is the type of thing that needs testing.

For what it's worth, the need is out there, there have been Twitter threads of devs spending too long on doing it manually, and that the tool isn't handy raises the barrier to entry to a more inclusive community, which sucks.

#### Update Jan 2nd:

It's January 2nd and also the program like 1/2 works! That's the update! One part of the refactor got done and the program doesn't crash, but it's sorting and acting needs a refactor now!

Dependencies come with it now! Much easier!

Just:

`pip install master-blaster`
`master-blaster`

Also, the code has been // TODO refactored to be more readable and testable, and //TODO testing has begun!
