from dataclasses import dataclass

@dataclass
class Student:
    """Class for keeping track of an item in inventory."""
    canvas_id: int
    cu_id: str
    name: str