from abc import ABC, abstractmethod
from src.assignment import Assigment
from src.student import Student
 
class Grader(ABC):
 
    @abstractmethod
    def grade(self, student, assignment) -> Grade:
        '''Assign a student a grade for the assignment on Canvas'''
        pass
 
