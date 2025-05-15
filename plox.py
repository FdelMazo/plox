#!/usr/bin/env python3

import sys
from plox.Scanner import Scanner
from plox.Parser import Parser

# usar prompt_toolkit si está disponible
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory

    use_prompt_toolkit = True
    promptsession = PromptSession(history=FileHistory(".plox_history"))
except ImportError:
    use_prompt_toolkit = False


class Plox:
    def __init__(self):
        self.mode = None  # "scanning" | "parsing"
        self.had_error = False

    def run(self, source: str):
        # IDEA: si esta en un modo particular, que las distintas fases
        # se pongan en modo debug, y vayan imprimiendo lo que hacen
        scanner = Scanner(source)

        try:
            tokens = scanner.scan()
        except Exception as e:
            self.had_error = True
            print(f"Scanning Error: {e}")
            return

        # en modo scanning, solo imprimimos los tokens
        if self.mode == "scanning":
            for i, token in enumerate(tokens):
                print(f"token {i}: {token}")
            return

        parser = Parser(tokens)
        try:
            expression = parser.parse()
        except Exception as e:
            self.had_error = True
            print(f"Parsing Error: {e}")
            return

        # en modo parsing, imprimimos las expresiones encontradas
        if self.mode == "parsing":
            print(expression)

    def main(self):
        if len(sys.argv) > 1:
            if sys.argv[1] == "--scanning":
                self.mode = "scanning"
            if sys.argv[1] == "--parsing":
                self.mode = "parsing"

        while True:
            try:
                source = (
                    promptsession.prompt("> ") if use_prompt_toolkit else input("> ")
                )
                if not source:
                    continue
            except (EOFError, KeyboardInterrupt):
                break

            self.run(source)
            self.had_error = False


if __name__ == "__main__":
    plox = Plox()
    plox.main()
