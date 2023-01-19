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
from src.vars import DATE_FORMAT

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

    def create(self, due: datetime, publish=False, points=3):

        title = datetime.strptime(due, DATE_FORMAT).strftime("%b. %d") + " Quiz"

        self.course.course.create_quiz(
            {
                "title": title,
                "published": publish,
                "time_limit": 5,
                "allowed_attempts": 1,
                "scoring_policy": "keep_average",
                "assignment_group_id": self.quiz_group,
                "points_possible": points,
                "due_at": due + "T" + self.course.config.end_time
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


def set_extra_time_on_quizzes(
    course, names, names2ids_course, extra_minutes=10
):
    """
    course = canvas.get_course(CUnum2canvasnum["3401"])
    names = [o.replace('\n', "") for o in open("accomodations3401.txt")]
    names2ids_course = names2ids["3401"]

    To see this in the Canvas UI click "Moderate this quiz"
    https://community.canvaslms.com/t5/Instructor-Guide/Once-I-publish-a-quiz-how-can-I-give-my-students-extra-attempts/ta-p/1242
    $ canvas -set_extra_time_on_quizzes -c 3401
    """
    ids = [names2ids_course[i] for i in names]

    for quiz in course.get_quizzes():
        print("[*] Setting accomodation for {}".format(quiz.title))
        for id_ in ids:
            print("-", id_)
            quiz.set_extensions([{"user_id": id_, "extra_time": extra_minutes}])