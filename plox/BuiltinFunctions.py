from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Interpreter import Interpreter

from .Function import Function


class BuiltinFunction(Function):
    """Clase base para todas las funciones nativas de Lox.
    BuiltinFunction hereda de Function para mantener la interfaz común
    """

    def __init__(self, arity: int, name: str, params: str = ""):
        self.arity = arity
        self.name = name
        self.params = params

    def __call__(self, interpreter: "Interpreter", arguments: list):
        raise NotImplementedError("Builtin functions must implement __call__")

    def __repr__(self) -> str:
        if self.params:
            return f"<builtin fn {self.name}({self.params})>"
        return f"<builtin fn {self.name}>"


class TypeFunction(BuiltinFunction):
    """Built-in function that returns the type of a value as a string."""

    def __init__(self):
        super().__init__(arity=1, name="type", params="value")

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
        elif isinstance(value, BuiltinFunction):
            return "builtin function"
        elif isinstance(value, Function):
            return "function"
        else:
            return "unknown"