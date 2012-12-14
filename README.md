chess
=====

Chess Project for AI Fundamentals (Python)


___ Running The Code ___
There are four primary scripts in the ./bin folder:
 - runServer.sh:       Runs a MaverickChess server, required for the players to run
 - runHuman.sh:        Human player which allows you to play a game on the server manually
 - runAI-random.sh:    AI that randomly chooses moves from the possible choices
 - runAI.sh:           The actual AI that was the focus of this project

The server and client will not run without installing the Twisted package, included
in the ./lib directory, on your system. Instructions can be found in the INSTALL text
file contained within the archive. This was required to rapidly create a reasonably
solid network-capable system.

There is no need to compile, although deleting .pyc files may fix errors:
 find . -name '*.pyc' -print -delete



___ READ THIS: Git ___ ***
By the nature of such a project, we had a stable and a development branch. What
you see shown is the stable branch, since we wanted you to see the latest version
of the code. However, the ./.git directory holds all of the branches and versions
of our code. Therefore, here are a few git commands that will give you more view
into our system:

git checkout master             # Check out the development branch
git checkout functional         # Check out the stable branch

# View a log of all contributions to the project (James mostly at the end, Matt mostly at the beginning):
git log --graph --all --abbrev-commit --pretty=format:'%C(yellow)%h %Creset%C(green)%cr %C(blue)%an%C(bold red)%d%Creset %s'

Each of the branches and versions contains the same scripts, but only the
functional branch contains the latest versions of the reports.



___ Reading the Reports ___
There are a few reports (with some shared content):
 - ./docs/Presentations/Final Report:
   The primary write-up for this project
 - ./docs/Presentations/Midpoint Report:
   The mid-point status report we submitted to you
 - ./docs/Specifications:
   Planning documents from early in the semester (some plans changed)
 - README.md:
   This readme



___ Other Project Pieces ___
./src:    The code for the project
./extras: Some internal references we used
./lib:    Library we used for network code (must be installed as specified above)
