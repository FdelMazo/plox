import sys
import subprocess
import os

LOX_BINARY = "plox"

for lox_file in filter(lambda f: f.endswith(".lox"), os.listdir("real-tests")):
    print(f"$ {LOX_BINARY} real-tests/{lox_file}")
    result = subprocess.run(
        [LOX_BINARY, f"real-tests/{lox_file}"],
        stdout=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
    )
    out = result.stdout.decode().strip()
    print(out)
    print()
    if "ERROR".lower() in out.lower():
        sys.exit(1)
