from typing import Any


def is_valid_dict_key(*values: Any):
    return all(
        isinstance(value, str)
        or isinstance(value, int)
        or isinstance(value, float)
        or isinstance(value, bool)
        or value is None
        for value in values
    )


def is_numeric_index(indexable_length: int, *indexs: Any):
    def _is_numeric_index(index, indexable_length):
        if not (int(index) == index and index >= 0):
            return False

        index = int(index)
        # Revisamos que no esté fuera de rango
        if index >= indexable_length:
            return False

        return True

    return all(_is_numeric_index(index, indexable_length) for index in indexs)
