
from typing import List
from src.config import Config
from datetime import datetime
from canvasapi.canvas import Canvas
from pathlib import Path
from src.api import get_api
from datetime import timedelta
from src.course import Course
from datetime import datetime
from tqdm import tqdm as tqdm

class Assignment(object):


    def __init__(self, course, assignment_id):
        self.assignment = course.course.get_assignment(assignment_id)
        self.full_credit = self.assignment.points_possible

    def get_submissions(self):
        return [j for j in self.assignment.get_submissions()]

    def grade_based_on_participation(self):
        '''
        - Assign full credit to everyone who submitted
        - Assign zeros to students who did not submit
        '''

        submissions = self.get_submissions()

        for submission in tqdm(submissions):
            if submission.missing:
                submission.edit(
                    submission={"posted_grade": 0},
                    comment={"text_comment": "no submission"},
                )
            else:
                submission.edit(
                    submission={"posted_grade": self.full_credit},
                    comment={"text_comment": "Full credit"},
                )
        print(f"[*] Graded {len(submissions)} based on participation")

if __name__ == "__main__":
    path = Path("/Users/abe/CanvasCLI/3220S2023.ini")
    config = Config(path)
    api = get_api()
    course = Course(config=config, api=api)
    assignment = Assignment(course=course,
                            assignment_id=1607592)

    assignment.grade_based_on_participation()
