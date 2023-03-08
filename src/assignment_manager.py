'''
Stuff for managing assignments that is the assignment itself
'''
from typing import List
from src.config import Config
from datetime import datetime
from canvasapi.canvas import Canvas
from pathlib import Path
from src.api import get_api
from src.course import Course
from datetime import timedelta
from src.course import Course
from datetime import datetime

class AssignmentManager(object):

    def __init__(self, course: Course):
        self.course = course
        self.config = course.config
        self.assignment_groups = course.assigment_groups

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


    def create(self,
               due: datetime,
               group: str):

        title = group + " " + due.strftime("%b %d")

        self.course.course.create_assignment(
                {
                    "name": title,
                    "published": False,
                    "due_at": due.strftime("%Y-%m-%d") + "T23:59:00",
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

            self.course.course.create_assignment(
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
