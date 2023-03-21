import unittest
from src.auto_graded_notebook import Notebook
from src.auto_graded_notebook import NotebookParser

class TestAutogradedNotebook(unittest.TestCase):

    def test_rule_based_model_runs_predict_proba(self):

        parser = NotebookParser("test/fixtures/four.ipynb")
        cells = parser.parse()
        notebook = Notebook(cells)
        assert notebook.all_missing_points_are_not_implemented(assigned_score=9, max_score=10)


    '''
    def test_sum_to_ten(self):

        parser = NotebookParser("test/fixtures/nine.ipynb")
        cells = parser.parse()
        notebook = Notebook(cells)
        assert sum(o.points for o in notebook.cells) == 10
    '''

    def test_has_1_point_5(self):
        parser = NotebookParser("test/fixtures/nine.ipynb")
        cells = parser.parse()
        notebook = Notebook(cells)
        assert any(i.points == 1.5 for i in notebook.cells)

    def test_has_with_id(self):
        parser = NotebookParser("test/fixtures/nine.ipynb")
        cells = parser.parse()
        notebook = Notebook(cells)
        assert any(i.id == "0f11489a-a716-4edf-8bf6-56689cd9a0df" for i in notebook.cells)


    def test_has_with_id(self):
        parser = NotebookParser("test/fixtures/nine.ipynb")
        cells = parser.parse()
        notebook = Notebook(cells)
        _id = "0f11489a-a716-4edf-8bf6-56689cd9a0df"
        target_cell = [_ for _ in notebook.cells if _.id == _id]
        assert len(target_cell) == 1

    def test_has_with_id_right_points(self):
        parser = NotebookParser("test/fixtures/nine.ipynb")
        cells = parser.parse()
        notebook = Notebook(cells)
        _id = "0f11489a-a716-4edf-8bf6-56689cd9a0df"
        target_cell = [_ for _ in notebook.cells if _.id == _id][0]
        assert target_cell.points==1.5


    def test_attempted_but_missed(self):
        parser = NotebookParser("test/fixtures/nine.ipynb")
        cells = parser.parse()
        notebook = Notebook(cells)
        assert notebook.attempted_last_but_missed(8.5, 10)