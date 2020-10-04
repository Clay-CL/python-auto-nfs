import os

p = 'D:/python-projs/python-auto-nfs/raw-images/'

for count, filename in enumerate(os.listdir(p)):
    dst = str(count) + ".jpg"
    src = p + filename
    dst = p + dst

    # rename() function will
    # rename all the files
    os.rename(src, dst)
