from abc import ABC, abstractmethod


class BaseAI(ABC):
    """Every AI provider in this system must implement generate()."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Send a prompt to the AI provider and return its raw text response.
        """
        raise NotImplementedError
