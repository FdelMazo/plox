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
        match value:
            case bool():
                return "bool"
            case int() | float():
                return "number"
            case str():
                return "string"
            case None:
                return "nil"
            case _ if isinstance(value, BuiltinFunction):
                return "builtin function"
            case _ if isinstance(value, Function):
                return "function"
            case dict():
                return "dictionary"
            case list():
                return "array"
            case _:
                return "unknown"


class LenFunction(BuiltinFunction):
    """Built-in function that returns the len of a string"""

    def __init__(self):
        super().__init__(arity=1, name="len", params="value")

    def __call__(self, interpreter: "Interpreter", arguments: list):
        """
        Return the length of the first argument if it is a string
        Raises an error if the argument is not a string
        """

        value = arguments[0]
        match value:
            case str() as string:
                return len(string)
            case dict() as dictionary:
                return len(dictionary)
            case list() as lst:
                return len(lst)
            case _:
                raise RuntimeError(
                    f"Argument of `len` must be an array, dict or string, got: {value}"
                )


class KeysFunction(BuiltinFunction):
    """Funcion built-in que devuelve las keys del primer argumento"""

    def __init__(self):
        super().__init__(arity=1, name="keys", params="value")

    def __call__(self, interpreter: "Interpreter", arguments: list):
        """
        Devuelve las keys del primer argumento
        Lanza un error si el argumento no es compatible
        """

        value = arguments[0]
        match value:
            case dict() as dictionary:
                return list(dictionary.keys())
            case _:
                raise RuntimeError(
                    f"Argument of `keys` must be a dictionary, got: {value}"
                )


class ValuesFunction(BuiltinFunction):
    """Funcion built-in que devuelve los values del primer argumento"""

    def __init__(self):
        super().__init__(arity=1, name="values", params="value")

    def __call__(self, interpreter: "Interpreter", arguments: list):
        """
        Devuelve los values del primer argumento
        Lanza un error si el argumento no es compatible
        """

        value = arguments[0]
        match value:
            case dict() as dictionary:
                return list(dictionary.values())
            case _:
                raise RuntimeError(
                    f"Argument of `dict_values` must be a dictionary, got: {value}"
                )
