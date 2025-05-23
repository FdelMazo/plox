from typing import Optional


class Env(object):
    def __init__(self, *, enclosing: Optional["Env"] = None):
        self._values: dict[str, object] = {}
        # El entorno global es el único que no tiene enclosing
        self.enclosing: Optional["Env"] = enclosing

    def __repr__(self) -> str:
        return f"Environment: {self._values}{f' (Enclosing{self.enclosing})' if self.enclosing else ''}"

    def define(self, name: str, value: object):
        # No estamos chequeando si la variable ya esta definida.
        # Lox nos permite hacer var x = 1; var x = 2;
        # mientras que otros lenguajes lo consideran un error
        self._values[name] = value

    def get(self, name: str) -> object:
        if name in self._values:
            return self._values[name]

        # Si no encontré la variable, le pregunto al entorno padre
        if self.enclosing is not None:
            return self.enclosing.get(name)

        # Lox considera un error el intentar referenciar una
        # variable inexistente
        # una opción mucho más permisiva habria sido devolver Nil,
        # en estos casos
        raise RuntimeError(f"Undefined variable '{name}'")

    def assign(self, name: str, value: object) -> object:
        if name in self._values:
            self._values[name] = value
            return value

        # Si no encontré la variable, le pregunto al entorno padre
        if self.enclosing is not None:
            return self.enclosing.assign(name, value)

        raise RuntimeError(f"Cannot assign to undefined variable '{name}'")
