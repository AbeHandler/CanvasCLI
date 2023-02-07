from src.config import Config
from canvasapi.canvas import Canvas
from pathlib import Path
from src.api import get_api
from src.student import Student
from src.grade_enum import LetterGrade
from typing import List

from src.assignment import Assignment

class Course(object):

    def __init__(self, config: Config, api: Canvas):
        self.config = config
        self.course = api.get_course(config.canvas_no)
        self.course_name = config.course_name
        self.assigment_groups = {i.name: i.id for i in self.course.get_assignment_groups()}
        self.students = None

    def get_front_page(self):
        '''The main page always has the course_name'''
        return self.course.get_page(self.course_name)

    def get_quiz(self, quiz_id):
        return self.course.get_quiz(quiz_id)

    def export(self):
        """This will create a course backup on Canvas"""
        self.course.export_content(export_type="common_cartridge")

    def get_assignment_by_id(self, assignment_id: int):
        return self.course.get_assignment(assignment_id)

    def get_assignment_group(self, assignment_group: str):
        self._validate_assignment_group(assignment_group)
        return self.assigment_groups[assignment_group]

    def get_assignments_in_group(self, assignment_group: str) -> List[Assignment]:
        group_id = self.get_assignment_group(assignment_group)
        out = []
        canvas_assignments = [_ for _ in self.course.get_assignments_for_group(group_id)]
        for canvas_assignment in canvas_assignments:
            canvas_id = canvas_assignment.id
            assignment = Assignment(course=self,
                                    assignment_id=canvas_assignment.id)
            out.append(assignment)
        return out

    def lookup_assignment_id(self, assignment_group: str, assignment_name: str) -> int:
        """Get the ID of an assignment by group/assignment name

        This function is used to quickly find an assignment_id
        instead of opening Canvas to look. Looping over all assignments
        in the API is slow so instead only loop over assignments
        in the assignment_group

        Args:
            assignment_group (str) : group name in Canvas, e.g. "Exercises"
            assignment_name (str) : assignment name in Canvas, e.g. "Week 01 Assignment"

        Returns:
            assignment_id(int) : ID of assignment in canvas

        Raises:
            ValueError: If group does not exist, or there is no assignment
            with that name in the group
        """

        assignments = self.get_assignments_in_group(assignment_group)
        self._validate_assignment_name(assignments, assignment_name, assignment_group)
        return next(o.id for o in assignments if o.name == assignment_name)

    def get_letter_grades(self) -> List:
        '''
        Get a list of current grades for students

        The enrollments object has a current_grade field 
        which is score on graded assigments so far, as
        oppoesed to grades on all assignments in class
        '''
        grades = []
        enollments = self.course.get_enrollments()
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


    def _validate_assignment_group(self, group: str):
        if not group in self.assigment_groups.keys():
            raise ValueError(f"There is no assignment group {group}")

    def _validate_assignment_name(self, assignments, assignment_name, assignment_group):
        assignment_names = [o.name for o in assignments]
        if not assignment_name in assignment_names:
            raise ValueError(f"There is no {assignment_name} in group {assignment_group}")

    def get_students(self):
        '''Create a list of students in the course'''
        students = []
        for student in self.course.get_recent_students():
            name = student.name
            canvas_id = student.id
            cu_id = student.login_id
            student = Student(name=name,
                              canvas_id=canvas_id,
                              cu_id=cu_id)
            students.append(student)
        return students

    def lookup_student_by_cu_id(self, cu_id: str):
        if self.students is None:
            self.students = self.get_students()
        return next(i for i in self.students if i.cu_id == cu_id)

if __name__ == "__main__":
    path = Path("/Users/abe/CanvasCLI/3220S2023.ini")
    config = Config(path)
    api = get_api()
    course = Course(config=config, api=api)
    print(course.get_average_grade())