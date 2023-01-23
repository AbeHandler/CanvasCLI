from typing import List
from pathlib import Path
from src.assignment import Assignment
import os
import sys


class NBGraderManager():
    '''
    Python code to manage interactions with NBGrader
    '''
    def __init__(self, 
                 nb_grader_assignment_name: str = "one",
                 path_to_autograded: Path = Path("/Users/abe/everything/teaching/S2023/3220/3220/autograded"),
                 path_to_autograde_script: Path = Path("/Users/abe/everything/teaching/S2023/3220/3220/autograde.sh")):
        '''
        Initializes the manager

        Args:
            nb_grader_assignment_name: an assignment name in an nbgrader project
            path_to_autograded: path_to nbgrader's autograded directory
            path_to_autograde_script: path_to script that runs nbgrader's autograde.
            the script is to avoid including dependence on nbgrader in the main python package
        '''
        self.path_to_autograde_script = path_to_autograde_script
        self.nb_grader_assignment_name = nb_grader_assignment_name
        self.path_to_autograded = path_to_autograded

    def run(self):
        self._run_nb_grader()
        self._run_py_files()
        # TODO return list of grades

    def _run_nb_grader(self):
        cd = "cd " + Path(self.path_to_autograde_script).parents[0].as_posix()
        cmd = f"{cd} && sh {self.path_to_autograde_script.as_posix()} {self.nb_grader_assignment_name}"
        os.system(cmd)

    def _get_autograded_files(self) -> List[str]:
        out = []
        for p in self.path_to_autograded.rglob("*.py"):
            if self.nb_grader_assignment_name in p.as_posix():
                out.append(p)
        return out

    def _run_py_files(self):

        for file in self._get_autograded_files():
            output = file.parents[0] / (self.nb_grader_assignment_name + ".txt")

            cmd = f"python {file.as_posix()} > {output.as_posix()} \n"

            sys.stderr.write(cmd)
            os.system(cmd)
        

if __name__ == '__main__':
    nb_grader = NBGraderManager()
    nb_grader.run()

