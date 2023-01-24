from canvasapi.submission import Submission as CanvasSubmission
from src.grade import Grade
from src.student import Student

class UngradedSubmission():
    '''
    Not alll submissions are graded. Some are just submitted.
    '''


    def __init__(self, student: Student,
    				   submission: CanvasSubmission
    			 ):
        self.submission = submission
        self.student = student
