#!/usr/bin/env python3

import sys
import argparse
from plox.Scanner import Scanner
from plox.Parser import Parser
from plox.Interpreter import Interpreter

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
            return

        interpreter = Interpreter()
        try:
            interpreter.interpret(expression)
        except Exception as e:
            self.had_error = True
            print(f"Runtime Error: {e}")
            return

    def main(self):
        parser = argparse.ArgumentParser(
            prog="plox",
            description="Lox interpreter in Python",
        )
        options = parser.add_mutually_exclusive_group()
        options.add_argument(
            "--scanning", action="store_true", help="Run in scanning mode"
        )
        options.add_argument(
            "--parsing", action="store_true", help="Run in parsing mode"
        )
        parser.add_argument(
            "file", nargs="?", help="Interpret a file instead of running the REPL"
        )

        args = parser.parse_args()

        if args.scanning:
            self.mode = "scanning"
        elif args.parsing:
            self.mode = "parsing"

        if args.file:
            with open(args.file, "r") as file:
                # Acá estamos haciendo uso de que Python ya sabe dividir archivos en lineas,
                # pero lo correcto sería manejar correctamente los \n en el scanner de lox
                for line in file:
                    print(f"> {line.strip()}")
                    self.run(line.strip())
            return

        while True:
            try:
                source = (
                    promptsession.prompt("> ") if use_prompt_toolkit else input("> ")
                )
            except (EOFError, KeyboardInterrupt):
                break

            self.run(source)
            self.had_error = False


if __name__ == "__main__":
    plox = Plox()
    plox.main()
