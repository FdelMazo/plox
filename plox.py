#!/usr/bin/env python3

import traceback
import argparse
from plox.PrettyPrinter import PrettyPrinter
from plox.Scanner import Scanner
from plox.Parser import Parser
from plox.Resolver import Resolver
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
        self.debug = False
        self.mode = None  # "scanning" | "parsing" | "resolve"
        self.interpreter = Interpreter()
        self.printer = PrettyPrinter(
            branch_f=lambda s: colored(s, "white"),
            expr_f=lambda s: colored(s, "light_yellow"),
            stmt_f=lambda s: colored(s, "red"),
            type_f=lambda s: colored(s, "light_blue"),
        )

    def run(self, source: str):
        scanner = Scanner(source)
        try:
            tokens = scanner.scan()
        except Exception as e:
            if self.debug:
                traceback.print_exc()
            print(colored(f"Scanning Error: {e}", "light_red"))
            return

        # en modo scanning, solo imprimimos los tokens
        if self.mode == "scanning":
            for token in tokens:
                print(colored(repr(token), "light_blue"))
            return

        parser = Parser(tokens)
        try:
            statements = parser.parse()
        except Exception as e:
            if self.debug:
                traceback.print_exc()
            print(colored(f"Parsing Error: {e}", "light_red"))
            return

        # en modo parsing, imprimimos las expresiones encontradas
        if self.mode == "parsing":
            self.printer.print(statements)
            return

        resolver = Resolver(self.interpreter)
        for statement in statements:
            try:
                resolver.resolve(statement)
                # Proponemos manejar los warnings simplemente imprimiendolos
                print(resolver.get_warnings_report())
            except Exception as e:
                if self.debug:
                    traceback.print_exc()
                print(colored(f"Resolve Error: {e}", "light_red"))

        # en modo resolve, imprimimos los scopes locales del intérprete
        if self.mode == "resolve":
            print(
                colored(
                    f"Interpreter Locals: {self.interpreter.local_scope_depths}",
                    "light_blue",
                )
            )
            return

        try:
            self.interpreter.interpret(statements)
        except Exception as e:
            if self.debug:
                traceback.print_exc()
            print(colored(f"Runtime Error: {e}", "light_red"))
            return

    def main(self):
        parser = argparse.ArgumentParser(
            prog="plox",
            description="Lox interpreter in Python",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Print error stack traces",
        )

        options = parser.add_mutually_exclusive_group()
        options.add_argument(
            "--scanning", action="store_true", help="Run in scanning mode"
        )
        options.add_argument(
            "--parsing", action="store_true", help="Run in parsing mode"
        )
        options.add_argument(
            "--resolve", action="store_true", help="Run in resolve mode"
        )
        parser.add_argument(
            "--line-by-line", action="store_true", help="Run in line-by-line mode"
        )
        parser.add_argument(
            "file", nargs="?", help="Interpret a file instead of running the REPL"
        )

        args = parser.parse_args()

        if args.debug:
            self.debug = True

        if args.scanning:
            self.mode = "scanning"
        elif args.parsing:
            self.mode = "parsing"
        elif args.resolve:
            self.mode = "resolve"

        if args.file:
            with open(args.file, "r") as file:
                # Modo line by line, sin tener en cuenta los saltos de linea
                # Acá estamos haciendo uso de que Python ya sabe dividir archivos en lineas
                if args.line_by_line:
                    for line in file:
                        print(f"> {line.strip()}")
                        self.run(line)
                # modo multi-linea por default
                else:
                    source = file.read()
                    self.run(source)

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
