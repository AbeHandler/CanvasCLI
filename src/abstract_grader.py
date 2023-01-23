from abc import ABC, abstractmethod
from src.assignment import Assignment
from src.student import Student
from src.grade import Grade
 
class AbstractGrader(ABC):
 
    @abstractmethod
    def grade(self, student, assignment) -> Grade:
        '''Assign a student a grade for the assignment on Canvas'''
        pass
 
