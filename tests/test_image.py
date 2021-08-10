# simple test of image tool
# requires files/bucky*.png

from image import image

i = image("files/bucky*.gif")

# These methods should be obsolete
# i.convert("files/bucky*.gif", "tmp*.png")
# i.montage("", "files/bucky*.gif", "tmp*.png", "tmpnew*.gif")
# i.view("*.gif")

print("all done")
