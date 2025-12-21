from typing import Optional


class Env(object):
    def __init__(self, *, enclosing: Optional["Env"] = None):
        self.values: dict[str, object] = {}
        # El entorno global es el único que no tiene enclosing
        self.enclosing: Optional["Env"] = enclosing

    def __repr__(self) -> str:
        all_values = str(self.values)
        enclosing = self.enclosing
        while enclosing is not None:
            all_values += " << " + str(enclosing.values)
            enclosing = enclosing.enclosing
        return all_values

    def define(self, name: str, value: object):
        # No estamos chequeando si la variable ya esta definida.
        # Lox nos permite hacer var x = 1; var x = 2;
        # mientras que otros lenguajes lo consideran un error
        self.values[name] = value

    def get(self, name: str) -> object:
        if name in self.values:
            return self.values[name]

        # Si no encontré la variable, le pregunto al entorno padre
        if self.enclosing is not None:
            return self.enclosing.get(name)

        # Lox considera un error el intentar referenciar una
        # variable inexistente
        # una opción mucho más permisiva habria sido devolver Nil,
        # en estos casos
        raise RuntimeError(f"Undefined variable '{name}'")

    def assign(self, name: str, value: object) -> object:
        if name in self.values:
            self.values[name] = value
            return value

        # Si no encontré la variable, le pregunto al entorno padre
        if self.enclosing is not None:
            return self.enclosing.assign(name, value)

        raise RuntimeError(f"Cannot assign to undefined variable '{name}'")
