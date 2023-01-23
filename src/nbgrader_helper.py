from abc import ABC, abstractmethod
from src.assignment import Assigment
from src.student import Student
from src.grader import AbstractGrader
 
class NBGrader(AbstractGrader):
    '''
    This is a helper class for nbgrader

    It uses a bash script to run nbgrader to avoid
    a dependency on nbgrader package in main package
    '''
 
    def grade(self, student, assignment) -> Grade:
        '''Assign a student a grade for the assignment on Canvas'''
        pass


 
