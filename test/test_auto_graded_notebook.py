import unittest
from src.auto_graded_notebook import NotebookCell
from src.auto_graded_notebook import Notebook
from src.auto_graded_notebook import NotebookParser

class TestAutogradedNotebook(unittest.TestCase):

    def test_rule_based_model_runs_predict_proba(self):

	    parser = NotebookParser("test/fixtures/four.ipynb")
	    cells = parser.parse()
	    notebook = Notebook(cells)
	    assert notebook.all_missing_points_are_not_implemented(assigned_score=9, max_score=10)