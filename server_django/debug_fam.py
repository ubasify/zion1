import os

path = r'c:\Users\oladi\sources\rccghgz\server_django\templates\people\member_family.html'

with open(path, 'rb') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if b'member.last_name' in line:
        print(f"Line {i+1}: {line}")
        print(f"Repr: {repr(line)}")
