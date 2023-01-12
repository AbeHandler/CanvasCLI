
from typing import List
from src.config import Config
from datetime import datetime
from canvasapi.canvas import Canvas
from pathlib import Path
from src.api import get_api
from src.course import Course

class AssignmentManager(object):

    def __init__(self, config: Config, api: Canvas, assignment_group: str):
        ### to get assigmnent group see print_assignment_groups
        self.config = config
        self.course = api.get_course(config.canvas_no)
        self.assignment_group = assignment_group # e.g. 216448

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


    def create_assignment(self, duedate: datetime, title: str):

        self.course.create_assignment(
                {
                    "name": title,
                    "published": False,
                    "due_at": duedate.strftime("%Y-%m-%d") + "T23:59:00",
                    "points_possible": 10,
                    "description": title,
                    "assignment_group_id": self.assignment_group,
                    "submission_types": ["online_upload", "online_text_entry"],
                }
            )

if __name__ == "__main__":
    path = Path("/Users/abe/CanvasCLI/3220S2023.ini")
    config = Config(path)
    api = get_api()
    course = Course(config=config, api=api)

    from datetime import datetime

    now = datetime.now()
    assignment = AssignmentManager(config, api, "263527")
    assignment.create_assignment(now, "test")
