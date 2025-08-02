import re
piece = "我是<ft color=(224,164,25) color=(224,164,25)>七画"

a = re.search(r"<ft(.*)>", piece)
for param in a.group(1).split():
    print(param)

start, end = a.span()
print(start)
print(end)

print(piece[:start])