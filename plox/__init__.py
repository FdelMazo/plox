from .BuiltinFunctions import (
    LenFunction,
    TypeFunction,
    KeysFunction,
    ValuesFunction,
    ItemsFunction,
    AppendFunction,
    RemoveFunction,
    InsertFunction,
    SearchFunction,
    ContainsFunction,
    SortFunction,
)


BUILTIN_FUNCTIONS = {
    func.name: func for func in (
        LenFunction(),
        TypeFunction(),
        KeysFunction(),
        ValuesFunction(),
        ItemsFunction(),
        AppendFunction(),
        RemoveFunction(),
        InsertFunction(),
        SearchFunction(),
        ContainsFunction(),
        SortFunction(),
    )
}
