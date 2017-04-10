# Return type from IO functions

from enum import Enum


class ResultType(Enum):
    Ok = 0
    Err = 1


class Result:
    def __init__(self, result, value):
        self.result = result
        self.value = value

    def __str__(self):
        result = "Ok" if self.result == ResultType.Ok else "Err"
        value = str(self.value) if self.value is not None else "None"
        return "Result of type: " + result + " with value: " + value

    def is_ok(self):
        return self.result == ResultType.Ok

    def is_err(self):
        return self.result == ResultType.Err

    def get_ok(self):
        return self.value if self.result == ResultType.Ok else None

    def get_err(self):
        return self.value if self.result == ResultType.Err else None

    __repr__ = __str__
