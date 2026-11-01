import sys, os
os.chdir('..')
content = open('src/views/result.php', encoding='utf-8').read()
lines = content.split('\n')
for i, l in enumerate(lines[114:125], 115):
    print(i, repr(l))
