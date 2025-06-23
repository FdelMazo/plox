#!/usr/bin/env python3
import traceback
import argparse
from src.compiler.Scanner import Scanner
from src.compiler.Compiler import Compiler
from src.Chunk import Chunk
from src.run.VM import VM


class Plox:
    def run(self, chunk: Chunk):
        vm = VM(chunk)
        vm.run()

    def compile(self, source: str):
        scanner = Scanner(source)
        try:
            tokens = scanner.scan()
        except Exception as e:
            traceback.print_exc()
            print(f"Scanning Error: {e}")
            return None

        compiler = Compiler(tokens)
        try:
            chunk = compiler.compile()
        except Exception as e:
            traceback.print_exc()
            print(f"Compilation Error: {e}")
            return None

        return chunk

    def interpret(self, source: str):
        chunk = self.compile(source)
        if chunk:
            chunk.dis()
            self.run(chunk)

    def main(self):
        parser = argparse.ArgumentParser(
            prog="plox",
            description="Lox arithmetic expressions interpreter with a bytecode compilation step.",
        )
        parser.add_argument(
            "file",
            nargs="?",
            help="Interpret a file line by line instead of running the REPL",
        )

        args = parser.parse_args()
        if args.file:
            with open(args.file, "r") as file:
                for line in file:
                    print(f"> {line.strip()}")
                    self.interpret(line.strip())
            return

        while True:
            try:
                source = input("> ")
            except KeyboardInterrupt:
                break

            self.interpret(source)


if __name__ == "__main__":
    plox = Plox()
    plox.main()
