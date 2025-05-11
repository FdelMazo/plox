#!/usr/bin/env python3

import sys
from pylox.Scanner.Scanner import Scanner

# usar prompt_toolkit si está disponible
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory

    use_prompt_toolkit = True
    promptsession = PromptSession(history=FileHistory(".pylox_history"))
except ImportError:
    use_prompt_toolkit = False


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
            source = promptsession.prompt("> ") if use_prompt_toolkit else input("> ")
            self.run(source)
            self.had_error = False


if __name__ == "__main__":
    pylox = Pylox()
    pylox.main()
