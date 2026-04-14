from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Interpreter import Interpreter

from .Function import Function


class TypeFunction(Function):
    """Built-in function that returns the type of a value as a string."""

    def __init__(self):
        self.arity = 1

    def __call__(self, interpreter: "Interpreter", arguments: list):
        """Return the type of the first argument as a string."""
        value = arguments[0]

        #  bool es una subclase de int en Python (por eso checkeo primero eso)
        if isinstance(value, bool):
            return "bool"
        elif isinstance(value, (int, float)):
            return "number"
        elif isinstance(value, str):
            return "string"
        elif value is None:
            return "nil"
        elif isinstance(value, Function):
            return "function"
        else:
            return "unknown"

    def __repr__(self) -> str:
        return "<fn type>"
