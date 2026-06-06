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
    "len": LenFunction(),
    "type": TypeFunction(),
    "keys": KeysFunction(),
    "values": ValuesFunction(),
    "items": ItemsFunction(),
    "append": AppendFunction(),
    "remove": RemoveFunction(),
    "insert": InsertFunction(),
    "search": SearchFunction(),
    "contains": ContainsFunction(),
    "sort": SortFunction(),
}
