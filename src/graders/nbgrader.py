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
from src.auto_graded_notebook import Notebook
from src.auto_graded_notebook import NotebookParser
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
                 feedback_location: str,
                 nbgrader_name: str,
                 autograded_location: str,
                 max_score: int = 10):
        assignment = Assignment(course=course, assignment_id=assignment_id)
        grades = []
        with open(grades_location, "r") as inf:
            for _ in inf:
                grades.append(json.loads(_))
        self.grades = grades
        self.course = course
        self.assignment = assignment
        self.feedback_location: Path = Path(feedback_location)
        self.autograded_location: Path = Path(autograded_location)
        self.nbgrader_name = nbgrader_name
        self.filename = f"{nbgrader_name}.ipynb"
        self.max_score = max_score

    def _get_grades_for_assignment(self, assignment: str):
        return [_ for _ in self.grades if _["assignment"] == assignment and _["student_id"] != "akh2103"]

    def _get_perfect_scores(self, assignment: str):
        '''
        assignment is nbgrader name, e.g. "one"
        '''
        assignment_scores = self._get_grades_for_assignment(assignment)
        assert len(assignment_scores) > 0, f"Could not fild assignment {assignment}. Are you using nbgrader name?"
        perfects = [_ for _ in assignment_scores if _["score"] == _["max_score"]]
        return perfects

    def _get_non_perfect_scores(self, assignment: str):
        '''
        assignment is nbgrader name, e.g. "one"
        '''
        assignment_scores = self._get_grades_for_assignment(assignment)
        assert len(assignment_scores) > 0, f"Could not fild assignment {assignment}. Are you using nbgrader name?"
        not_perfects = [_ for _ in assignment_scores if _["score"] != _["max_score"]]
        return not_perfects

    def grade_skipped(self, assignment: str, dryrun: bool = True) -> None:
        missings = self._get_non_perfect_scores(assignment)
        count = 0

        for missing in missings:
            score = missing["score"]
            cu_id = missing['student_id']
            path_to = (self.autograded_location / cu_id / assignment / self.filename).as_posix()
            try:
                parser = NotebookParser(path_to)
                notebook = parser.get_notebook()

                notimplemented = notebook.all_missing_points_are_not_implemented(assigned_score=score,
                                                                                 max_score=self.max_score)
                if notimplemented:
                    count += 1
                if dryrun and notimplemented:
                    print(f"did not implement: {cu_id}")
                if notimplemented and not dryrun:
                    comment = "Some problems not attempted, otherwise correct"
                    grade = Grade(score=score, comments=[comment])
                    student = self.course.lookup_student_by_cu_id(cu_id)
                    submission = self.assignment.assignment.get_submission(student.canvas_id)
                    submission = Submission(student=student,
                                            submission=submission,
                                            grade=grade)
                    submission.sync()
            except KeyError:
                print(f"[*] Error for for {cu_id}")
            except FileNotFoundError:
                print(f"[*] Could not find submission for {cu_id}")
        prefix = "Autograded" if not dryrun else "Dryrun: planning to autograde"
        print(f"[*] {prefix} {count} students who did not attempt some problems")

    def grade_missed_challenge(self, assignment: str, dryrun: bool = True) -> None:
        count = 0

        for missing in self._get_non_perfect_scores(assignment):
            score = missing["score"]
            cu_id = missing['student_id']
            path_to = (self.autograded_location / cu_id / assignment / self.filename).as_posix()
            try:
                parser = NotebookParser(path_to)
                notebook = parser.get_notebook()
                attempted_last_but_missed = notebook.attempted_last_but_missed(assigned_score=score,
                                                                               max_score=self.max_score)
                if attempted_last_but_missed:
                    count += 1
                if dryrun and attempted_last_but_missed:
                    print(f"Got all but challenge: {cu_id}")
                if attempted_last_but_missed and not dryrun:
                    comment = "Attempted challenge, but not correct. Otherwise all correct. 1/2 credit for challenge"
                    score += (self.max_score - score)/2
                    grade = Grade(score=score, comments=[comment])
                    student = self.course.lookup_student_by_cu_id(cu_id)
                    submission = self.assignment.assignment.get_submission(student.canvas_id)
                    submission = Submission(student=student,
                                            submission=submission,
                                            grade=grade)
                    submission.sync()
            except KeyError:
                print(f"[*] Key error for {cu_id}")
            except FileNotFoundError:
                print(f"[*] Could not find submission for {cu_id}")
        prefix = "Autograded" if not dryrun else "Dryrun: planning to autograde"
        print(f"[*] {prefix} {count} students who attempted challenge but was not correct")


    def grade_perfect_scores(self, assignment: str, dryrun: bool = False):
        perfects = self._get_perfect_scores(assignment)
        notperfects = self._get_non_perfect_scores(assignment)

        if dryrun:
            Nperfects = len(perfects)
            Nnotperfects = len(notperfects)
            print(f"[*] {Nperfects} got perfect scores; ending early for dryrun")
            print(f"[*] {Nnotperfects} got not perfect scores; ending early for dryrun")
            import os; os._exit(0)

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


    def grade_not_perfect_scores(self, assignment: str, partial_credit: float = 0.0):
        not_perfects = self._get_non_perfect_scores(assignment)

        for perfect in tqdm(not_perfects, desc=f"Assigning not perfect scores with patial credit {partial_credit}"):

            try:
                cu_id = perfect['student_id']
                feedback_path = Path(self.feedback_location / cu_id / assignment/ f"{assignment}.html")
                print(feedback_path)

                if feedback_path.is_file():
                    feedback = Feedback(feedback_path)
                    student = self.course.lookup_student_by_cu_id(cu_id)
                    submission = self.assignment.assignment.get_submission(student.canvas_id)
                    score = feedback.score
                    missing_points = self.max_score - score
                    partial_credit_points = missing_points * partial_credit

                    comments=["Please see attached report. "]

                    if partial_credit > 0:
                        comments.append(f"For this assignment, we assigned {partial_credit} for missed questions.")
                    else:
                        comments.append(f"The class average was pretty high for this assignment. So we did not assign partial credit for missed questions.")

                    comments.append("Please send a Canvas message to the instructor or TA if you have any questions about your grade.")

                    grade = Grade(score=score + partial_credit_points, comments=comments)

                    submission = Submission(student=student,
                                            submission=submission,
                                            grade=grade)

                    submission.sync()
                else:
                    print("No file file")
            except ValueError:
                print("ERROR", feedback_path)

    def get_class_average(self, assignment: str) -> float:
        '''
        assignment is the nbgrader name, e.g. "five" but not 194132
        '''        
        perfects = self._get_perfect_scores(assignment)
        nonperfects = self._get_non_perfect_scores(assignment)
        all_ = perfects + nonperfects

        perfect_points = sum(i["score"] for i in perfects)
        non_perfect_points = sum(i["score"] for i in nonperfects)
        total_points = sum(i["max_score"] for i in all_)
        return ((perfect_points + non_perfect_points)/total_points)

    def get_class_average_with_partial_credit(self, assignment: str, partial: float) -> float:
        '''
        assignment is the nbgrader name, e.g. "five" but not 194132
        '''        
        perfects = self._get_perfect_scores(assignment)
        nonperfects = self._get_non_perfect_scores(assignment)
        all_ = perfects + nonperfects

        perfect_points = sum(i["score"] for i in perfects)
        non_perfect_points = sum(i["score"] for i in nonperfects)
        partial_points = sum(partial * (i["max_score"] - i["score"]) for i in nonperfects)
        total_points = sum(i["max_score"] for i in all_)
        return ((perfect_points + non_perfect_points + partial_points)/total_points)

if __name__ == "__main__":
    path = Path("/Users/abe/CanvasCLI/3220F2023.ini")
    config = Config(path)
    api = get_api()
    
    course = Course(config=config, api=api)
    grader = NBGrader(course=course,
                      grades_location=config.path_to_grades,
                      assignment_id=1793764,
                      nbgrader_name='nine',
                      feedback_location=config.path_to_feedback,
                      max_score=25,
                      autograded_location=config.path_to_autograded)

    grader.grade_not_perfect_scores("nine")
