from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Interpreter import Interpreter

from .Function import Function
from .Utils import is_numeric_index, is_valid_dict_key


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
                raise RuntimeError(f"Argument of `len` must be an array, dict or string, got: {value}")


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


class ItemsFunction(BuiltinFunction):
    """Funcion built-in que devuelve los items del primer argumento"""

    def __init__(self):
        super().__init__(arity=1, name="items", params="value")

    def __call__(self, interpreter: "Interpreter", arguments: list):
        """
        Devuelve los items del primer argumento
        Lanza un error si el argumento no es compatible
        """

        value = arguments[0]
        match value:
            case dict() as dictionary:
                # Convertimos a una lista de lista ya que
                # de momento no implementamos tuplas
                return [[key, value] for key, value in dictionary.items()]
            case _:
                raise RuntimeError(
                    f"Argument of `items` must be a dictionary, got: {value}"
                )


class AppendFunction(BuiltinFunction):
    """
    Funcion built-in que agrega un elemento al primer argumento
    Devuelve una copia shallow del primer argumento con el elemento agregado
    Lanza un error si el primer argumento no es compatible
    """

    def __init__(self):
        super().__init__(arity=2, name="append", params="collection, value")

    def __call__(self, interpreter: "Interpreter", arguments: list):
        """
        Agrega el segundo argumento al primer argumento
        Lanza un error si el primer argumento no es compatbile
        """

        collection, value = arguments
        match collection:
            case list() as lst:
                lst_copy = lst.copy()
                lst_copy.append(value)
                return lst_copy
            case _:
                raise RuntimeError(
                    f"First argument of `append` must be an array, got: {collection}"
                )


class RemoveFunction(BuiltinFunction):
    """
    Funcion built-in que elimina un elemento del primer argumento
    Devuelve una copia shallow del primer argumento con el elemento eliminado
    Lanza un error si el primer argumento no es compatible
    """

    def __init__(self):
        super().__init__(arity=2, name="remove", params="collection, value")

    def __call__(self, interpreter: "Interpreter", arguments: list):
        """
        Elimina el segundo argumento del primer argumento
        Si el elemento no se encuentra en la lista, no hace nada
        Lanza un error si el primer argumento no es compatible
        """

        collection, value = arguments
        match collection:
            case list() as lst:
                if len(lst) == 0:
                    return lst

                lst_copy = lst.copy()

                for i in range(len(lst_copy)):
                    if lst_copy[i] == value:
                        lst_copy.pop(i)
                        return lst_copy

            case dict() as dictionary:
                dict_copy = dictionary.copy()
                if value in dict_copy:
                    del dict_copy[value]
                return dict_copy

            case _:
                raise RuntimeError(
                    f"First argument of `remove` must be an array or dictionary, got: {collection}"
                )


class SearchFunction(BuiltinFunction):
    """
    Funcion built-in que busca un elemento en el primer argumento y devuelve su índice
    Devuelve el índice del elemento si se encuentra, o nil si no se encuentra
    """

    def __init__(self):
        super().__init__(arity=2, name="search", params="collection, value")

    def __call__(self, interpreter: "Interpreter", arguments: list):
        """
        Busca el segundo argumento en la lista pasada como primer argumento
        Devuelve el índice del elemento si se encuentra, o nil si no se encuentra
        Lanza un error si el primer argumento no es compatible
        """

        collection, value = arguments
        match collection:
            case list() as lst:
                for i in range(len(lst)):
                    if lst[i] == value:
                        return i
                return None
            case _:
                raise RuntimeError(
                    f"First argument of `search` must be an array, got: {collection}"
                )


class InsertFunction(BuiltinFunction):
    """
    Funcion built-in que inserta un elemento en una lista en un índice dado
    Devuelve una copia shallow del primer argumento con el elemento insertado
    Lanza un error si el primer argumento no es compatible o
    si el segundo argumento no es valido ante el primer argumento
    """

    def __init__(self):
        super().__init__(arity=3, name="insert", params="collection, index, value")

    def __call__(self, interpreter: "Interpreter", arguments: list):
        """
        Inserta el tercer argumento en el primer argumento en el índice dado por el segundo argumento
        Lanza un error si el primer argumento no es compatible o
        si el segundo argumento no es valido ante el primer argumento
        """

        collection, index, value = arguments
        match collection:
            case list() as lst:
                array_length = len(lst) + 1
                if not is_numeric_index(array_length, index):
                    raise RuntimeError(
                        f"Second argument of `insert` must be a number less than {array_length}, got: {index}"
                    )

                lst_copy = lst.copy()
                lst_copy.insert(int(index), value)
                return lst_copy

            case dict() as dictionary:
                if not is_valid_dict_key(index):
                    raise RuntimeError(
                        f"Second argument of `insert` must be a valid dictionary key, got: {index}"
                    )

                dict_copy = dictionary.copy()
                dict_copy[index] = value
                return dict_copy

            case _:
                raise RuntimeError(
                    f"First argument of `insert` must be an array or dictionary, got: {collection}"
                )


class ContainsFunction(BuiltinFunction):
    """Funcion built-in que verifica si un elemento se encuentra en una colección"""

    def __init__(self):
        super().__init__(arity=2, name="contains", params="collection, value")

    def __call__(self, interpreter: "Interpreter", arguments: list):
        """
        Verifica si el segundo argumento se encuentra en el primer argumento
        Devuelve true si se encuentra, false si no se encuentra
        Lanza un error si el primer argumento no es compatible
        """

        collection, value = arguments
        match collection:
            case list() as lst:
                return value in lst
            case dict() as dictionary:
                return value in dictionary
            case _:
                raise RuntimeError(
                    f"First argument of `contains` must be an array or dictionary, got: {collection}"
                )


class SortFunction(BuiltinFunction):
    """
    Funcion built-in que ordena el primer argumento
    Devuelve una copia shallow del primer argumento ordenada
    Lanza un error si el primer argumento no es compatible
    """

    def __init__(self):
        super().__init__(arity=1, name="sort", params="collection")

    def __call__(self, interpreter: "Interpreter", arguments: list):
        """
        Ordena el primer argumento
        Lanza un error si el primer argumento no es compatible
        """

        collection = arguments[0]
        match collection:
            case list() as lst:
                return sorted(lst)
            case dict() as dictionary:
                return dict(sorted(dictionary.items()))
            case _:
                raise RuntimeError(
                    f"First argument of `sort` must be an array or dictionary, got: {collection}"
                )
