import random
from pathlib import Path
from src.config import Config
from src.api import get_api
from src.course import Course

from datetime import datetime
from enum import Enum

class QuestionType(Enum):
    CALCULATED = "calculated_question"
    ESSAY = "essay_question"
    FILE_UPLOAD = "file_upload_question"
    FILL_IN_MULTIPLE_BLANKS = "fill_in_multiple_blanks_question"
    MATCHING = "matching_question"
    MULTIPLE_ANSWERS = "multiple_answers_question"
    MULTIPLE_CHOICE = "multiple_choice_question"
    MULTIPLE_DROPDOWNS = "multiple_dropdowns_question"
    NUMERICAL = "numerical_question"
    SHORT_ANSWER = "short_answer_question"
    TEXT_ONLY = "text_only_question"
    TRUE_FALSE = "true_false_question"

class Quiz(object):

    def __init__(self, course, quiz_id):
        self.course = course
        self.quiz_id = quiz_id
        self._quiz = course.get_quiz(quiz_id)
        self.title = self._quiz.title

    def create_question_group(self, group_name: str, 
                              pick_count: int = 1,
                              question_points: str = 5):
        group = {"name": group_name, 
                 "pick count": pick_count,
                 "question points": question_points}
        self._quiz.create_question_group(quiz_groups=[group])


    def create_question(self, question_name: str,
                        question_text: str,
                        question_type: QuestionType,
                        points_possible: int = 4):
        
        print(question_type.value)

        question_data = {
            'question': {
                'question_name': question_name,
                'question_text': question_text,
                'points_possible': points_possible,
                "question_type": question_type.value
            }
        }

        print(question_data)
        self._quiz.create_question(**question_data)

    def get_submissions(self):
        return [o for o in self._quiz.get_submissions()]

    @staticmethod
    def init_quizzes_for_day(course, day: str=None, participation="Most meals?"):
        if day is None:
            day = datetime.now().strftime("%b. %d")

        for quiz in course.get_quizzes(day):
            quiz = Quiz(course, quiz.id)
            q = quiz.create_question(question_name="Main question",
                                     question_text="What does the code print?",
                                     points_possible=6,
                                     question_type=QuestionType.NUMERICAL)

            q = quiz.create_question(question_name="Participation",
                                     question_text="Most sleep?",
                                     points_possible=2,
                                     question_type=QuestionType.NUMERICAL)

            print(quiz)

if __name__ == "__main__":
    path = Path("/Users/abe/CanvasCLI/3220F2023.ini")
    config = Config(path)
    api = get_api()
    course = Course(config=config, api=api)
    from src.calendar import get_dates_for_course
    for ino, d in enumerate(get_dates_for_course(config)):
        if ino > 6:
            Quiz.init_quizzes_for_day(course, d["date"].strftime("%b. %d"))



