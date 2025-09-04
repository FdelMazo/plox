from __future__ import annotations
from abc import abstractmethod, ABC


class Visitable(ABC):
    @abstractmethod
    def accept[R](self, visitor: Visitor[R]) -> R:
        pass


class Visitor[R](ABC):
    @abstractmethod
    def accept_binary(self, visitor: Visitable) -> R:
        pass
