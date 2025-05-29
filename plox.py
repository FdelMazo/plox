#!/usr/bin/env python3

import sys
import argparse
from plox.Scanner import Scanner
from plox.Parser import Parser
from plox.Interpreter import Interpreter

# usar prompt_toolkit y termcolor si están disponibles
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from termcolor import colored

    promptsession = PromptSession(history=FileHistory(".plox_history"))

    def prompt_input():
        return promptsession.prompt("> ")

except ImportError:

    def colored(text, _):
        return text

    def prompt_input():
        return input("> ")


class Plox:
    def __init__(self):
        self.mode = None  # "scanning" | "parsing"

    def run(self, source: str):
        scanner = Scanner(source)

        try:
            tokens = scanner.scan()
        except Exception as e:
            print(colored(f"Scanning Error: {e}", "light_red"))
            return

        # en modo scanning, solo imprimimos los tokens
        if self.mode == "scanning":
            for i, token in enumerate(tokens):
                print(colored(f"token {i}: {token}", "light_blue"))
            return

        parser = Parser(tokens)
        try:
            expression = parser.parse()
        except Exception as e:
            print(colored(f"Parsing Error: {e}", "light_red"))
            return

        # en modo parsing, imprimimos las expresiones encontradas
        if self.mode == "parsing":
            print(colored(expression, "light_blue"))
            return

        interpreter = Interpreter()
        try:
            interpreter.interpret(expression)
        except Exception as e:
            print(colored(f"Runtime Error: {e}", "light_red"))
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
                source = prompt_input()
            except (EOFError, KeyboardInterrupt):
                break

            self.run(source)


if __name__ == "__main__":
    plox = Plox()
    plox.main()
