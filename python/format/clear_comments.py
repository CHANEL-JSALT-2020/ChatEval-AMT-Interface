import re

matcher = re.compile(r'.*, None\?\n')

f = open("comments.txt", 'r')
coms = f.readlines()
f.close()

cleared = []

for i in range(0, len(coms), 2):
    mat = matcher.match(coms[i+1])
    if mat is None:
        cleared.append(coms[i+1])

f = open('comments_cleaned.txt', 'w')
f.writelines(cleared)
f.close()