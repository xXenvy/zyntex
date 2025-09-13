from abc import ABC, abstractmethod


class INodeElement(ABC):
    """Base class for all Zig AST node wrappers."""

    @abstractmethod
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"INodeElement.{self.__class__.__name__}"

    @classmethod
    @abstractmethod
    def from_node(cls, node):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def is_node_valid(node) -> bool:
        raise NotImplementedError
