from .BuiltinFunctions import (
    LenFunction,
    TypeFunction,
    KeysFunction,
    ValuesFunction,
)


BUILTIN_FUNCTIONS = {
    func.name: func
    for func in (
        LenFunction(),
        TypeFunction(),
        KeysFunction(),
        ValuesFunction(),
    )
}
