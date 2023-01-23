from src.abstract_grader import AbstractGrader
from typing import List
from pathlib import Path
from src.assignment import Assignment
import os
import sys



class NBGrader(AbstractGrader):
    def __init__(self, 
                 assignment_name: str = "one",
                 path_to_autograded: Path = Path("/Users/abe/everything/teaching/S2023/3220/3220/autograded"),
                 path_to_autograde_script: Path = Path("/Users/abe/everything/teaching/S2023/3220/3220/autograde.sh")):
        # the script is to avoid including dependence on nbgrader in the main python package
        self.path_to_autograde_script = path_to_autograde_script
        self.assignment_name = assignment_name
        self.path_to_autograded = path_to_autograded

 
    # overriding abstract method
    def grade(self):
        cd = "cd " + Path(self.path_to_autograde_script).parents[0].as_posix()
        cmd = f"{cd} && sh {self.path_to_autograde_script.as_posix()} {self.assignment_name}"
        os.system(cmd)


    def get_autograded_files(self,
                             assignment_name: str,
                             path_to_autograded: Path) -> List[str]:

        out = []
        for p in path_to_autograded.rglob("*.py"):
            if assignment_name in p.as_posix():
                out.append(p)
        return out

    def run_py_files(self):

        for file in self.get_autograded_files(assignment_name=self.assignment_name,
                                              path_to_autograded=self.path_to_autograded):
            output = file.parents[0] / (self.assignment_name + ".txt")

            cmd = f"python {file.as_posix()} > {output.as_posix()} \n"

            sys.stderr.write(cmd)
            os.system(cmd)
        

if __name__ == '__main__':
    nb_grader = NBGrader()
    #nb_grader.grade()
    nb_grader.run_py_files()

