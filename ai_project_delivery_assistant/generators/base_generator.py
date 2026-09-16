from abc import ABC, abstractmethod
from docx import Document


class BaseGenerator(ABC):
    """
    Shared shape for every document generator in this project.
    Salvaged from the old project - this pattern worked cleanly there.
    """

    def __init__(self):
        self.document = Document()

    @abstractmethod
    def build(self, data: dict):
        """Fill self.document with content, using the given structured data."""
        raise NotImplementedError

    def save(self, output_file: str):
        self.document.save(output_file)

    def generate(self, data: dict, output_file: str):
        self.build(data)
        self.save(output_file)
