
from typing import List

class Assignment(object):

    def __init__(self, config: Config, api: Canvas):
        self.config = config
        self.course = api.get_course(config.canvas_no)

    def get_no_submissions(assignment) -> List:
        """
        Get students who did not submit

        This is old code and I am not sure what "assignment" is 
        """
        assignment = self.course.get_assignment(assignment)
        non_submitting_students = []
        for student in assignment.get_gradeable_students():
            id_ = student.id
            submission = assignment.get_submission(id_)
            if submission.submitted_at is None:
                non_submitting_students.append(student)
        return non_submitting_students