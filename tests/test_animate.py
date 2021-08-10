# simple test of animate tool
# requires files/bucky*png files

# Things to correct:
#   - The animation should go back and forth.It does not for now.
#   - The main window contains nothing.
#   - The animation does not start when opened.

from animate import animate

a = animate("files/bucky*gif")

print("all done")
