#!/usr/bin/env python3

import sys
from pylox.Scanner.Scanner import Scanner


class Pylox:
    def __init__(self):
        self.mode = None  # "scanning"
        self.had_error = False

    def run(self, source: str):
        scanner = Scanner(source)

        try:
            tokens = scanner.tokens()
        except Exception as e:
            self.had_error = True
            print(f"Scanning Error: {e}")
            return

        # en modo scanning, solo imprimimos los tokens
        if self.mode == "scanning":
            for i, token in enumerate(tokens):
                print(f"token {i}: {token}")
            return

    def main(self):
        if len(sys.argv) > 1 and sys.argv[1] == "--scanning":
            self.mode = "scanning"

        while True:
            source = input("> ")
            if not source:
                return

            self.run(source)
            self.had_error = False


if __name__ == "__main__":
    pylox = Pylox()
    pylox.main()
