import traceback
import argparse
from plox.Scanner import Scanner
from plox.Parser import Parser
from plox.Interpreter import Interpreter

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from termcolor import colored
from pathlib import Path
from platformdirs import user_data_dir


history_file = Path(user_data_dir("plox", ensure_exists=True)) / ".plox_history"
promptsession: PromptSession[str] = PromptSession(history=FileHistory(history_file))


class Plox:
    def __init__(self):
        self.debug = False
        self.mode = None  # "scanning" | "parsing"
        self.interpreter = Interpreter()

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
                print(colored(f"line {token.line} | {token}", "light_blue"))
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
            for i, statement in enumerate(statements):
                print(colored(statement, "light_blue"))
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

        if args.file:
            with open(args.file, "r") as file:
                # Modo line by line, sin tener en cuenta los saltos de linea
                # Acá estamos haciendo uso de que Python ya sabe dividir archivos en lineas
                if args.line_by_line:
                    for line in file:
                        if self.mode:
                            print(f"> {line.strip()}")
                        self.run(line)
                # modo multi-linea por default
                else:
                    source = file.read()
                    self.run(source)

            return

        while True:
            try:
                source = promptsession.prompt("> ")
            except (EOFError, KeyboardInterrupt):
                break

            self.run(source)


def main():
    plox = Plox()
    plox.main()


if __name__ == "__main__":
    main()
