import json
from collections import Counter
from typing import Union


def pytest_assertrepr_compare(config, op, left, right):
    if (isinstance(left, Unordered) or isinstance(right, Unordered)) and op == "==":
        return Unordered.assert_repr(left, right, config.getoption('verbose'))


class Unordered:
    # TODO docstring

    def __init__(self, iterable):
        self.iterable = iterable

    @classmethod
    def assert_repr(cls, left, right, verbose: int = 0):
        # TODO verbose
        left_items = left.iterable if isinstance(left, cls) else left
        right_items = right.iterable if isinstance(right, cls) else right
        return [
            f"{left} == {right}",
            f"items of {left_items} != items of {right_items}",
        ]

    def __str__(self):
        return f"{self.__class__.__name__}({self.iterable})"

    def __eq__(self, other: list):
        return self._counter(self.iterable) == self._counter(other)

    @staticmethod
    def _counter(iterable):

        def hashable_item(item):
            try:
                hash(item)
                return item
            except TypeError:
                # TODO nested Unordered
                if isinstance(item, (list, tuple)):
                    return tuple(map(hashable_item, item))
                elif isinstance(item, dict):
                    return frozenset(map(hashable_item, item.items()))
                return json.dumps(item)

        return Counter(map(hashable_item, iterable))


class SuperSet:
    # TODO docstring

    def __init__(self, collection: Union[dict, set]):
        self.collection = collection

    def __eq__(self, other):  # other is a superset of self.collection
        if isinstance(self.collection, set) and isinstance(other, set):
            return all(key in other for key in self.collection)
        elif isinstance(self.collection, dict) and isinstance(other, dict):
            return all(other[key] == val for key, val in self.collection.items())
        else:
            return False
