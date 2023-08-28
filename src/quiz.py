import random
from pathlib import Path
from src.config import Config
from src.api import get_api
from src.course import Course

class Quiz(object):

    def __init__(self, course, quiz_id):
        self.course = course
        self.quiz_id = quiz_id
        self._quiz = course.get_quiz(quiz_id)

    def create_question_group(self, group_name: str, 
                              pick_count: int = 1,
                              question_points: str = 5):
        group = {"name": group_name, 
                 "pick count": pick_count,
                 "question points": question_points}
        self._quiz.create_question_group(quiz_groups=[group])


    def create_question(self, question_name: str = "Lorem impsum",
                        question_text: str = 'What is Lorem impsum?',
                        points_possible: int = 4):
        id_ = random.randint(0, 10000) # TODO how to assign id_ in a pricipled way
        print(question_name, question_text)

        question_data = {
            'question': {
                'question_name': question_name,
                'question_text': question_text,
                'points_possible': points_possible,
                "question_type": "numerical_question",
                #'answers': [
                #    {'answer_text': 'Choice 1', 'weight': 100}
                #]
            }
        }

        print(question_data)
        self._quiz.create_question(**question_data)

if __name__ == "__main__":
    path = Path("/Users/abe/CanvasCLI/3220F2023.ini")
    config = Config(path)
    api = get_api()
    course = Course(config=config, api=api)
    quiz = Quiz(course, 337161)
    q = quiz.create_question(question_name="Participation",
                             question_text="tess2ts")
