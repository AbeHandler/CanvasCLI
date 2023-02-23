from typing import Dict, List
import json

class NotebookCell:
    def __init__(self, cell_type: str, execution_count: int, id: str, metadata: Dict, outputs: List, source: List[str]):
        self.cell_type = cell_type
        self.execution_count = execution_count
        self.id = id
        self.metadata = metadata
        self.outputs = outputs
        self.source = source

'''
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
'''

class NotebookParser:
    def __init__(self, filepath):
        self.filepath = filepath

    def parse(self) -> List[NotebookCell]:
        out = []
        with open(self.filepath, "r") as inf:
            dt = json.load(inf)
            for cell in dt["cells"]:
                cell = self.create_notebook_cell(cell)
                out.append(cell)
        return out
    
    def create_notebook_cell(self, cell):
        cell_type = cell["cell_type"]
        try:
            execution_count = cell["execution_count"]
        except:
            execution_count = 0
        _id = cell["id"]
        metadata = cell["metadata"]
        try:
            outputs = cell["outputs"]
        except:
            outputs = []
        source = cell["source"]
        
        return NotebookCell(cell_type, execution_count, _id, metadata, outputs, source)

if __name__ == "__main__":

    parser = NotebookParser("test/fixtures/four.ipynb")
    cells = parser.parse()
    cells[0].metadata
