import random

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
                        question_text: str = 'What is Lorem impsum?'):
        id_ = random.randint(0, 10000) # TODO how to assign id_ in a pricipled way
        self._quiz.create_question(**{"id": id_, 
                                      "quiz_id": self.quiz_id, 
                                      "question_name": question_name, 
                                      "question_text": question_text})

if __name__ == "__main__":
    path = Path("/Users/abe/CanvasCLI/3220S2023.ini")
    config = Config(path)
    api = get_api()
    course = Course(config=config, api=api)
    quiz = Quiz(course, 308165)
