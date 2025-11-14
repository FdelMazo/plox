class BuiltinFunction:
    def __init__(self, name, arity, impl):
        self.name = name
        self.arity = arity
        self._impl = impl

    def __call__(self, interpreter=None, arguments=None):
        # Los argumentos ya fueron chequeados contra self.arity
        return self._impl(*arguments)

    def __repr__(self) -> str:
        return f"<builtin {self.name}/{self.arity}>"


def _rand(max_value):
    if max_value <= 0:
        raise ValueError("max_value must be greater than 0")

    import random
    return random.randint(0, int(max_value) - 1)

def _time():
    import time
    return time.time()

def _sqrt(value):
    if value < 0:
        raise ValueError("Cannot compute square root of negative number")

    import math
    return math.sqrt(value)

__builtins__ = {
    "rand": BuiltinFunction("rand", 1, _rand),
    "time": BuiltinFunction("time", 0, _time),
    "sqrt": BuiltinFunction("sqrt", 1, _sqrt),
}

def is_builtin(name):
    return name in __builtins__

def get_builtin(name):
    return __builtins__[name]
