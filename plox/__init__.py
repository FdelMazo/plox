from .BuiltinFunctions import *

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
