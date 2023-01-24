from canvasapi.submission import Submission as CanvasSubmission
from src.grade import Grade
from src.student import Student
from src.submission import Submission

class GradedSubmission(Submission):
    '''
    Not alll submissions are graded. Some are just submitted.
    '''


    def __init__(self, student: Student,
    				   submission: CanvasSubmission,
    				   grade: Grade = None
    			 ):
        print(type(submission))
        assert type(submission) == CanvasSubmission
        super().__init__(student, submission)
        self.student = student
        self.grade = grade

    def sync(self):
            super().submission.edit(
                                 submission={"posted_grade": self.grade.score},
                                 comment={"text_comment": "\n".join(self.grade.comments)},
                                )
