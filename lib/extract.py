import inspect
from typing import TypeVar

T = TypeVar("T")


def extract_vars(cls: T, *args, **kwargs):
    return {
        key: (
            value.fget(*args, **kwargs)
            if isinstance(value, property)
            and value.fget != None
            and callable(value.fget)
            else value
        )
        for key, value in inspect.getmembers(cls)
        if not key.startswith("_") and not inspect.isfunction(value)
    }
