from typing import Optional


class Env(object):
    def __init__(self, *, enclosing: Optional["Env"] = None):
        self._values: dict[str, object] = {}
        # El entorno global es el único que no tiene enclosing
        self.enclosing: Optional["Env"] = enclosing

    def __repr__(self) -> str:
        return f"Environment: {self._values}{f' (Enclosing{self.enclosing})' if self.enclosing else ''}"

    def ancestor(self, distance: int) -> "Env":
        # Agarrar el scope a una distancia particular del actual
        env = self
        for _ in range(distance):
            if not env.enclosing:
                # Si el resolvedor de scopes y el intérprete están bien hechos,
                # este error no debería saltar nunca!
                raise RuntimeError(
                    f"No enclosing environment found for {self} at distance {distance}"
                )
            env = env.enclosing
        return env

    def define(self, name: str, value: object):
        # No estamos chequeando si la variable ya esta definida.
        # Lox nos permite hacer var x = 1; var x = 2;
        # mientras que otros lenguajes lo consideran un error
        self._values[name] = value

    def get(self, name: str, distance: int | None = None) -> object:
        scope = self

        # Si recibimos una distancia, nos movemos al scope correspondiente
        if distance is not None:
            scope = self.ancestor(distance)

        if name in scope._values:
            return scope._values[name]

        # Lox considera un error el intentar referenciar una
        # variable inexistente
        # una opción mucho más permisiva habria sido devolver Nil,
        # en estos casos
        raise RuntimeError(f"Undefined variable '{name}'")

    def assign(self, name: str, value: object, distance: int | None = None) -> object:
        scope = self

        # Si recibimos una distancia, nos movemos al scope correspondiente
        if distance is not None:
            scope = self.ancestor(distance)

        if name in scope._values:
            scope._values[name] = value
            return value

        # Si no encontramos la variable, lanzamos un error!
        raise RuntimeError(f"Cannot assign to undefined variable '{name}'")
