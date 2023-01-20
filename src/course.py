from src.config import Config
from canvasapi.canvas import Canvas
from pathlib import Path
from src.api import get_api
from src.grades import LetterGrade

class Course(object):

    def __init__(self, config: Config, api: Canvas):
        self.config = config
        self.course = api.get_course(config.canvas_no)
        self.course_name = config.course_name
        self.assigment_groups = {i.name: i.id for i in self.course.get_assignment_groups()}

    def get_front_page(self):
        '''The main page always has the course_name'''
        return self.course.get_page(self.course_name)

    def get_quiz(self, quiz_id):
        return self.course.get_quiz(quiz_id)

    def export(self):
        """This will create a course backup on Canvas"""
        self.course.export_content(export_type="common_cartridge")

    def print_assignment_groups(self):
        for i in self.course.get_assignment_groups():
            print(i)

    def get_assignment_group(self, group: str):
        return self.assigment_groups[group]

    def get_letter_grades(self):
        '''
        The enrollments object has a current_grade field 
        which is score on graded assigments so far
        This is the one to use
        '''

        grades = []
        enollments = course.course.get_enrollments()
        for ino, i in enumerate(enollments):
            try:
                grade = i.grades["current_grade"]
                grade = grade.replace("+", "_PLUS")
                grade = grade.replace("-", "_MINUS")
                grades.append(grade)
            except AttributeError:
                print("error")
        return grades

    def get_average_grade(self):

        letter_grades = self.get_letter_grades()
        total = sum([LetterGrade[i].value for i in letter_grades])
        return total/len(letter_grades)


if __name__ == "__main__":
    path = Path("/Users/abe/CanvasCLI/3220S2023.ini")
    config = Config(path)
    api = get_api()
    course = Course(config=config, api=api)
    print(course.get_average_grade())