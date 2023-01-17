
from typing import List
from src.config import Config
from datetime import datetime
from canvasapi.canvas import Canvas
from pathlib import Path
from src.api import get_api
from datetime import timedelta
from src.course import Course
from datetime import datetime

class AssignmentManager(object):

    def __init__(self,
                 config: Config, 
                 api: Canvas, 
                 assignment_groups: dict):
        self.config = config
        self.course = api.get_course(config.canvas_no)
        self.assignment_groups = assignment_groups

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


    def create_assignment(self,
                          duedate: datetime,
                          group: str,
                          title: str = None):

        if title is None:
            title = group + " " + duedate.strftime("%b %d")

        self.course.create_assignment(
                {
                    "name": title,
                    "published": False,
                    "due_at": duedate.strftime("%Y-%m-%d") + "T23:59:00",
                    "points_possible": 10,
                    "description": title,
                    "assignment_group_id": self.assignment_groups[group],
                    "submission_types": ["online_upload", "online_text_entry"],
                }
            )


    def init_assignments(self, first_due: datetime = None, points_possible: int = 10):
        """
        Init weekly assignments for a course
        """


        if first_due is None:
            date_counter = self.config.start_date
        else:
            date_counter = first_due

        for week in range(1, 17):
            title = "Week {} ".format(str(week).zfill(2)) + "Assignment"
            due_at = date_counter.strftime("%Y-%m-%d") + "T11:20:00"
            unlock_at = (date_counter - timedelta(days=7)).strftime("%Y-%m-%d") + "T11:00:00"

            self.course.create_assignment(
                {
                    "name": title,
                    "published": False,
                    "due_at": date_counter.strftime("%Y-%m-%d") + "T23:59:00",
                    "points_possible": 5,
                    "description": title,
                    "assignment_group_id": self.assignment_group,
                    "submission_types": ["online_upload"],
                }
            )
            date_counter = date_counter + timedelta(days=7)


if __name__ == "__main__":
    path = Path("/Users/abe/CanvasCLI/3220S2023.ini")
    config = Config(path)
    api = get_api()
    course = Course(config=config, api=api)
    groups = course.get_assignment_groups()

    manager = AssignmentManager(config, api, groups)

    manager.create_assignment(datetime(2023, 1, 17), group = "Interview grading")

    #start_date = datetime(2023, 1, 23)
    #manager.init_assignments(first_due = start_date)
