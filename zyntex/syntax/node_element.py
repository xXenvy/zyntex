from abc import ABC, abstractmethod


class INodeElement(ABC):
    """Base class for all Zig AST node wrappers."""

    @abstractmethod
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def is_node_valid(node) -> bool:
        raise NotImplementedError
