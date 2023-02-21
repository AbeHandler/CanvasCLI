from abc import ABC, abstractmethod
from src.assignment import Assignment
from src.student import Student
from src.grade import Grade
from src.course import Course
from random import shuffle
from pathlib import Path
from src.config import Config
from canvasapi.canvas import Canvas
from pathlib import Path
from src.api import get_api
from src.assignment import Assignment
from src.graders.nb_grader_feedback_file import Feedback
from tqdm import tqdm as tqdm
from src.submission import Submission
import json

class NBGrader(object):
    '''
    This is a helper class for nbgrader

    It uses a bash script to run nbgrader to avoid
    a dependency on nbgrader package in main package
    '''

    def __init__(self,
                 course: Course,
                 grades_location: str, 
                 assignment_id: int,
                 feedback_location: str):
        assignment = Assignment(course=course, assignment_id=assignment_id)
        grades = []
        with open(grades_location, "r") as inf:
            for _ in inf:
                grades.append(json.loads(_))
        self.grades = grades
        self.course = course
        self.assignment = assignment
        self.feedback_location: Path = Path(feedback_location)

    def _get_grades_for_assignment(self, assignment: str):
        return [_ for _ in self.grades if _["assignment"] == assignment and _["student_id"] != "akh2103"]

    def _get_perfect_scores(self, assignment: str):
        assignment_scores = self._get_grades_for_assignment(assignment)
        perfects = [_ for _ in assignment_scores if _["score"] == _["max_score"]]
        return perfects

    def _get_non_perfect_scores(self, assignment: str):
        assignment_scores = self._get_grades_for_assignment(assignment)
        not_perfects = [_ for _ in assignment_scores if _["score"] != _["max_score"]]
        return not_perfects

    def grade_perfect_scores(self, assignment: str):
        perfects = self._get_perfect_scores(assignment)
        comments = ["Nice job", "Good work", "Great"]

        for perfect in tqdm(perfects, desc="Assigning perfect scores"):
            score = perfect["score"]
            cu_id = perfect['student_id']
            shuffle(comments)
            comment = comments[0]
            grade = Grade(score=score, comments=[comment])
            student = self.course.lookup_student_by_cu_id(cu_id)
            submission = self.assignment.assignment.get_submission(student.canvas_id)
            submission = Submission(student=student,
                                    submission=submission,
                                    grade=grade)
            submission.sync()

        nperfects = len(perfects)
        print(f"[*] Graded {nperfects} perfects for assignment {assignment}")
 
    def _upload_report(self, assignment: str, submission):
        cu_id = submission['student_id']
        feedback_path = Path(self.feedback_location / cu_id / assignment/ f"{assignment}.html")
        
        if feedback_path.is_file():
            feedback = Feedback(feedback_path)
            student = self.course.lookup_student_by_cu_id(cu_id)
            submission = self.assignment.assignment.get_submission(student.canvas_id)
            
            submission = Submission(student=student,
                                    submission=submission)
            submission.add_attachment(feedback_path.as_posix())
            print(f"[*] added {feedback_path.as_posix()}")
        else:
            print(f"[*] could not file {feedback_path.as_posix()}")


    def upload_reports(self, assignment: str):
        '''
        assignment is the nbgrader name, e.g. "five" but not 194132
        '''

        submissions = self._get_grades_for_assignment(assignment)

        assert len(submissions) > 0, f"No grades for assignment {assignment}. Did you forget to run ./export.sh?"

        students = set([_['student_id'] for _ in submissions])

        students = list(students)
        students.sort()

        for student in tqdm(students, desc="Adding reports"):
            try:
                submissions_for_one_student = [j for j in submissions if j["student_id"] == student]
                assert len(submissions_for_one_student) == 1
                submission = submissions_for_one_student[0]
                assert submission["assignment"] == assignment
                self._upload_report(assignment=assignment, submission=submission)
            except ValueError:
                print("Error parsing ...")
                print(student)


    def grade_not_perfect_scores(self, assignment: str, min_score: int = 0):
        not_perfects = self._get_non_perfect_scores(assignment)


        not_perfects = not_perfects[6:]

        for perfect in tqdm(not_perfects, desc="Assigning not perfect scores"):
            
            cu_id = perfect['student_id']
            feedback_path = Path(self.feedback_location / cu_id / assignment/ f"{assignment}.html")
            
            if feedback_path.is_file():
                feedback = Feedback(feedback_path)
                student = self.course.lookup_student_by_cu_id(cu_id)
                submission = self.assignment.assignment.get_submission(student.canvas_id)
                comments=["Please see attached report", "Please send me a Canvas message if you have any questions about your grade."]
                if feedback.score < min_score:
                    score = min_score
                    comment ="5 points for attempting assignment"
                    comments.append(comment)
                else:
                    score = feedback.score

                grade = Grade(score=score, comments=comments)
                
                submission = Submission(student=student,
                                        submission=submission,
                                        grade=grade)

                submission.sync()
                submission.add_attachment(feedback_path.as_posix())


if __name__ == "__main__":
    path = Path("/Users/abe/CanvasCLI/3220S2023.ini")
    config = Config(path)
    api = get_api()
    
    course = Course(config=config, api=api)
    grader = NBGrader(course=course,
                      grades_location="/Users/abe/everything/teaching/S2023/3220/3220/grades.jsonl",
                      assignment_id=1589752,
                      feedback_location="/Users/abe/everything/teaching/S2023/3220/3220/feedback")
    grader.grade_not_perfect_scores(assignment="three", min_score = 5)