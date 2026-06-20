from typing import Any


def golden_rule_print(*args, **kwargs):
    transformed_args = (stringify(arg) for arg in args)

    print(*transformed_args, **kwargs)  # type: ignore


def stringify(value: Any) -> str:
    """
    Golden rule: Convierte cualquier valor de Python a una representación de cadena que se parezca a cómo se mostraría en Lox.
    """
    match value:
        case None:
            return "nil"
        case bool():
            return "true" if value else "false"
        case list():
            return f"[{', '.join(stringify(element) for element in value)}]"
        case dict():
            items = ", ".join(
                f"{stringify(k)}: {stringify(v)}" for k, v in value.items()
            )
            return f"{'[' + items + ']'}"
        case str():
            return f"'{value}'"
        case int() | float():
            if isinstance(value, float) and value.is_integer():
                return str(int(value))
            return str(value)
        case _:
            return str(value)
