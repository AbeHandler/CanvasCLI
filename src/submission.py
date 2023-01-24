from canvasapi.submission import Submission as CanvasSubmission
from src.grade import Grade
from src.student import Student

class Submission(object):


    def __init__(self, student: Student,
                       submission: CanvasSubmission
                 ):
        assert type(student) == Student
        self.student = student
        self.submission = CanvasSubmission