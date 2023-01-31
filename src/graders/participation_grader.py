from abc import ABC, abstractmethod
from src.assignment import Assignment
from src.student import Student
from src.grade import Grade
import sys
from typing import List
from src.config import Config
from datetime import datetime
from canvasapi.canvas import Canvas
from pathlib import Path
from src.api import get_api
from datetime import timedelta
from datetime import datetime
from tqdm import tqdm as tqdm
from typing import List
from src.student import Student
from tqdm import tqdm as tqdm
from src.graded_submission import GradedSubmission

class ParticipationGrader(object):
    '''
    Grade students based on participation
    '''
    def __init__(self, course, assignment):
        self.course = course
        self.students = course.get_students()
        self.assignment = assignment

    def grade_based_on_participation(self):
        '''
        - Assign full credit to everyone who submitted
        - Assign zeros to students who did not submit
        '''

        # TODO assignment should not really know about student
        # The assignment should not be in charge of grading itself

        submissions = [j for j in self.assignment.get_submissions(self.students)]

        for submission in tqdm(submissions):
            if submission.missing:
                grade = Grade(score=0, comments=["No submission"])
                submission = GradedSubmission(student=submission.student,
                                              submission=submission,
                                              grade=grade)
            else:
                grade = Grade(score=self.assignment.full_credit, comments=["Full credit"])
                submission = GradedSubmission(student=submission.student,
                                              submission=submission,
                                              grade=grade)
                submission.sync()

        print(f"[*] Graded {len(submissions)} based on participation")

if __name__ == "__main__":
    path = Path("/Users/abe/CanvasCLI/3220S2023.ini")
    config = Config(path)
    api = get_api()
    from src.course import Course
    course = Course(config=config, api=api)

    assignment = Assignment(course=course,
                            assignment_id=1620589)

    participation_grader = ParticipationGrader(course, assignment)
    participation_grader.grade_based_on_participation()