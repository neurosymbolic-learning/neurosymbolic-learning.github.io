from dataclasses import dataclass
from typing import Dict

from neurosym.types.type import Type


@dataclass(frozen=True, eq=True)
class Environment:
    """
    Represents a type environment containing the variables.
    """

    _elements: Dict[str, Type]

    @classmethod
    def empty(cls):
        return cls({})


@dataclass(frozen=True, eq=True)
class TypeWithEnvironment:
    """
    Represents a type in a given environment.
    """

    typ: Type
    env: Environment