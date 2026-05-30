# !/usr/bin/env python3
import sys
import subprocess
import os

# Recibe por argumento el comando para ejecutar el intérprete de Lox, por ejemplo:
# `./script.py plox`
# `./script.py ploxb`
# `./script.py "go run glox"`
# `./script.py "npm run jslox"`

LOX_BINARY = sys.argv[1].split() or ['plox']

currentdir = os.path.dirname(os.path.abspath(__file__))

for lox_file in filter(lambda f: f.endswith(".lox"), sorted(os.listdir(currentdir))):
    print(f"$ {' '.join(LOX_BINARY)} real-tests/{lox_file}")

    result = subprocess.run(
        [*LOX_BINARY, os.path.join(currentdir, lox_file)],
        stdout=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
    )

    out = result.stdout.decode().strip()
    print(out)
    print()

    if "ERROR".lower() in out.lower():
        sys.exit(1)

print(" -------- ")
print("| Todo OK |")
print(" -------- ")
