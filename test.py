
a = [1, 2, 3]

b = str(a)

c = [int(d) for d in b.replace('[', '').replace(']', '').replace(' ', '').split(',')]
print(a)
print(b)
print(c)

