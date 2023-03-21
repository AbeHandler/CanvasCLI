import json
from typing import Dict, List


class NotebookCell(object):
    def __init__(
        self,
        cell_type: str,
        execution_count: int,
        id: str,
        metadata: Dict,
        outputs: List,
        source: List[str],
        points: int,
        not_implemented: bool,
        rank: int,
    ):
        self.cell_type = cell_type
        self.execution_count = execution_count
        self.id = id
        self.metadata = metadata
        self.outputs = outputs
        self.source = source
        self.points = points
        self.not_implemented = not_implemented
        self.rank = rank


class Notebook(object):
    def __init__(self, cells: List[NotebookCell]) -> None:
        self.cells = cells

    def all_missing_points_are_not_implemented(
        self, assigned_score: int, max_score: int
    ) -> bool:
        not_implemented_deduction = 0
        for cell in self.cells:
            if cell.not_implemented:
                not_implemented_deduction += cell.points

        return assigned_score + not_implemented_deduction == max_score

    def _get_cells_with_points(self):
        return [i for i in self.cells if i.points != 0]

    def _get_last_graded(self) -> NotebookCell:
        graded = self._get_cells_with_points()
        graded.sort(key=lambda x: x.rank, reverse=True)
        return graded[0]

    def attempted_last_but_missed(self,
                                  assigned_score: int, 
                                  max_score: int) -> bool:
        last_graded_problem = self._get_last_graded()

        # if they implemented the last one
        if not last_graded_problem.not_implemented:
            # and the only thing missing is the last problem
            if assigned_score + last_graded_problem.points == max_score:
                return True

        return False


class NotebookParser(object):
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath

    def get_notebook(self) -> Notebook:
        cells = self.parse()
        return Notebook(cells)

    def parse(self) -> List[NotebookCell]:
        out = []
        with open(self.filepath, "r") as inf:
            dt = json.load(inf)
            for cellno, cell in enumerate(dt["cells"]):
                cell["rank"] = cellno
                cell = self.create_notebook_cell(cell)
                out.append(cell)
        return out

    def create_notebook_cell(self, cell: dict) -> NotebookCell:
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

        points = 0
        # not all cells are graded
        if "nbgrader" in metadata:
            if "points" in metadata["nbgrader"]:
                points = float(metadata["nbgrader"]["points"])

        not_implemented = False
        for _ in outputs:
            if "ename" in _:
                if _["ename"] == "NotImplementedError":
                    not_implemented = True

        return NotebookCell(
            cell_type,
            execution_count,
            _id,
            metadata,
            outputs,
            source,
            points,
            not_implemented,
            cell["rank"],
        )


if __name__ == "__main__":

    parser = NotebookParser("test/fixtures/four.ipynb")
    cells = parser.parse()
    notebook = Notebook(cells)
    print(
        notebook.all_missing_points_are_not_implemented(
            assigned_score=9, max_score=10
        )
    )

    print(notebook.get_last_graded())
