from abc import ABC, abstractmethod
from src.assignment import Assignment
from src.student import Student
from src.grade import Grade
from src.graders.abstract_grader import AbstractGrader

class Grader(AbstractGrader):
    '''
    This is a helper class for nbgrader

    It uses a bash script to run nbgrader to avoid
    a dependency on nbgrader package in main package
    '''
 
    def grade(self, student: Student, assignment: Assignment) -> Grade:
        '''Assign a student a grade for the assignment on Canvas'''
        pass


 
