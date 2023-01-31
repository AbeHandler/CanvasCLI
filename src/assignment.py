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

class Assignment(object):


    def __init__(self, course, assignment_id):
        self.assignment = course.get_assignment(assignment_id)
        self.full_credit = self.assignment.points_possible
        self.name = self.assignment.name
        self.id = self.assignment.id # the canvas id

    def get_submissions(self, students: List[Student]):
        submissions = [j for j in self.assignment.get_submissions()]
        
        out = []
        self._validate_get_submissions(students)
        for submission in submissions:

            student = [student for student in students if student.canvas_id == submission.user_id]
            if len(student) == 1:
                student = student[0]
                submission.student = student
                out.append(submission)
            else:
                sys.stderr.write(f"[*] Error on {submission}")
        return out

    def _validate_get_submissions(self, students):
        for student in students:
            assert type(student) == Student, str(student)


    def download_submissions(self,
                             students: List[Student],
                             expected_suffix: str = ".ipynb",
                             assignment_name: str = "one",
                             cannonical_file_name: str = "one.ipynb",
                             download_location: Path = "/Users/abe/everything/teaching/S2023/3220/3220"):
        '''
        - Download submissions that have the expected_suffix to download_location
        - Skip attachments that do not have the expected_suffix, and print alert
        - Download each file using the cannonical_file_name
        '''
        p = Path(download_location)
        p.mkdir(parents=True, exist_ok=True)
        sys.stderr.write(f"[*] Downloading to {p.as_posix()}")     
        submissions = self.get_submissions(students)
        total_downloaded = 0
        for submission in tqdm(submissions):
            attachments = submission.attachments
            attachments.sort(key = lambda x: x.updated_at_date, reverse=True)
            if len(attachments) > 0:
                latest = attachments[0]
                download_to = p / submission.student.cu_id / assignment_name
                download_to.mkdir(parents=True, exist_ok=True)
                if Path(latest.filename).suffix == expected_suffix:
                    latest.download((download_to / cannonical_file_name).as_posix())
                    total_downloaded += 1
                else:
                    print(f"[*] not sure about student {submission.student.name}, skipping")
        sys.stderr.write(f"[*] Downloaded {total_downloaded}")      
            

if __name__ == "__main__":
    path = Path("/Users/abe/CanvasCLI/3220S2023.ini")
    config = Config(path)
    api = get_api()
    from src.course import Course
    course = Course(config=config, api=api)
    assignment = Assignment(course=course,
                            assignment_id=1620589)
