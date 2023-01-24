from canvasapi.submission import Submission as CanvasSubmission
from src.grade import Grade
from src.student import Student

class GradedSubmission():
    '''
    Not alll submissions are graded. Some are just submitted.
    '''


    def __init__(self, student: Student,
    				   submission: CanvasSubmission,
    				   grade: Grade = None
    			 ):
        self.submission = submission
        self.student = student
        self.grade = grade

    def sync(self):
        self.submission.edit(submission={"posted_grade": self.grade.score},
                             comment={"text_comment": "\n".join(self.grade.comments)})
