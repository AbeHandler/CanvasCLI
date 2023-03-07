'''Code related to quizzes goes here'''

from typing import List
from src.config import Config
from datetime import datetime
from canvasapi.canvas import Canvas
from pathlib import Path
from src.api import get_api
from datetime import timedelta
from src.course import Course
from datetime import datetime
from src.config import STANDARDDATE

class QuizManager(object):
    '''
    Manages quizzes for a given group
    If you want to manage quizzes for a different group
    Make a new quiz manager
    '''

    def __init__(self,
                 quiz_group: str,
                 course: Course):
        self.course = course
        self.quiz_group = quiz_group

    def create(self, due: datetime, publish=False, points=3, time_limit: int = 5):

        title = due.strftime("%b. %d") + " Quiz"

        self.course.course.create_quiz(
            {
                "title": title,
                "published": publish,
                "time_limit": time_limit,
                "allowed_attempts": 1,
                "assignment_group_id": self.quiz_group,
                "points_possible": points,
                "due_at": due.strftime('%Y-%m-%d') + "T" + self.course.config.end_time
            }
        )
        print(f"[*] Created {title}")


if __name__ == "__main__":
    path = Path("/Users/abe/CanvasCLI/3220S2023.ini")
    config = Config(path)
    api = get_api()
     
    course = Course(config=config,
                    api=api)

    quiz_group = course.get_assignment_group("Quizzes")
    due = datetime(2023, 1, 17)
    manager = QuizManager(quiz_group, course)
    manager.create(due)
