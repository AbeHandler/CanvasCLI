from typing import Dict, List

class NotebookCell:
    def __init__(self, cell_type: str, execution_count: int, id: str, metadata: Dict, outputs: List, source: List[str]):
        self.cell_type = cell_type
        self.execution_count = execution_count
        self.id = id
        self.metadata = metadata
        self.outputs = outputs
        self.source = source

class Nbgrader:
    def __init__(self, cell_type: str, checksum: str, grade: bool, grade_id: str, locked: bool, points: int, schema_version: int, solution: bool, task: bool):
        self.cell_type = cell_type
        self.checksum = checksum
        self.grade = grade
        self.grade_id = grade_id
        self.locked = locked
        self.points = points
        self.schema_version = schema_version
        self.solution = solution
        self.task = task

class NotebookMetadata:
    def __init__(self, deletable: bool, editable: bool, execution: Dict, id: str, nbgrader: Nbgrader, tags: List[str]):
        self.deletable = deletable
        self.editable = editable
        self.execution = execution
        self.id = id
        self.nbgrader = nbgrader
        self.tags = tags

class Notebook:
    def __init__(self, cells: List[NotebookCell], metadata: NotebookMetadata, nbformat: int, nbformat_minor: int):
        self.cells = cells
        self.metadata = metadata
        self.nbformat = nbformat
        self.nbformat_minor = nbformat_minor
