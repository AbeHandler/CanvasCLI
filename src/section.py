from dataclasses import dataclass

@dataclass
class Section:
    """Class for keeping track of an item in inventory."""
    name: str
    section_id: int