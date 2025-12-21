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
        self.values[name] = value

    def get(self, name: str, distance: int | None = None) -> object:
        scope = self

        # Si recibimos una distancia, nos movemos al scope correspondiente
        if distance is not None:
            scope = self.ancestor(distance)

        if name in scope.values:
            return scope.values[name]

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

        if name in scope.values:
            scope.values[name] = value
            return value

        # Si no encontramos la variable, lanzamos un error!
        raise RuntimeError(f"Cannot assign to undefined variable '{name}'")
