from dataclasses import dataclass

@dataclass
class Section:
    """Class for keeping track of an item in inventory."""
    name: str
    section_id: int

    def __post_init__(self):
        # e.g. BAIM 3220-001 => 001
        self.name = str(int(self.name.split("-")[1]))


if __name__ == "__main__":
    section = Section(name="e-003", section_id=3)
    print(section)