import sys
import shutil
from datetime import datetime
from datetime import timedelta
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
from canvasapi.exceptions import ResourceDoesNotExist

class Assignment(object):


    def __str__(self):
        return f"{self.name}: {self.id}, due={self.due_at}"

    def __init__(self, course, assignment_id: int):
        self._validate_init(course)
        try:
            self.assignment = course.course.get_assignment(assignment_id)
        except ResourceDoesNotExist:
            raise ValueError(f"There is no assignment with ID {assignment_id}. Did you maybe pass a student ID?")
        self.name = self.assignment.name
        self.full_credit = self.assignment.points_possible
        self.name = self.assignment.name
        self.id = self.assignment.id # the canvas id

        # the Z on the end means zero time zone aka utz, -7 to get Denver time
        self.due_at = datetime.strptime(self.assignment.due_at, '%Y-%m-%dT%H:%M:%SZ') - timedelta(hours=7)

        self.graded_submissions_exist = self.assignment.graded_submissions_exist

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


    def _get_data_files(self, download_location, assignment_name) -> List[Path]:
        source_path = Path(download_location) / "source" / assignment_name
        source_path = source_path.as_posix()
        source_path = Path(source_path.replace("submitted/", ""))
        csvs = [j for j in source_path.glob('*.csv')]
        jsonls = [j for j in source_path.glob('*.jsonl')]
        data_files = csvs + jsonls
        return data_files

    def download_submissions(self,
                             students: List[Student],
                             expected_suffix: str = ".ipynb",
                             assignment_name: str = "one",
                             download_location: Path = "/Users/abe/everything/teaching/S2023/3220/3220",
                             cannonical_file_name = None):
        '''
        - Download submissions that have the expected_suffix to download_location
        - Skip attachments that do not have the expected_suffix, and print alert
        - Download each file using the cannonical_file_name
        '''
        p = Path(download_location)
        p.mkdir(parents=True, exist_ok=True)
        print(f"[*] Downloading to {p.as_posix()}")     
        submissions = self.get_submissions(students)
        total_downloaded = 0

        # many assignments have data files attached. These need to get copied over
        data_files = self._get_data_files(download_location, assignment_name)

        if cannonical_file_name is None:
            cannonical_file_name = f"{assignment_name}.ipynb"
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
                for data_file in data_files:
                    copied_file = download_to / data_file.name
                    print(data_file, copied_file)
                    shutil.copy(data_file, copied_file) 
        print(f"[*] Downloaded {total_downloaded} to {p.as_posix()}")

    def _validate_init(self, course):
        from canvasapi.course import Course
        if type(course) == Course:
            raise ValueError("Expected input of type src.course.Course not canvasapi.course.Course It's confusing.")

if __name__ == "__main__":
    path = Path("/Users/abe/CanvasCLI/3220S2023.ini")
    config = Config(path)
    api = get_api()
    from src.course import Course
    course = Course(config=config, api=api)
    assignment = Assignment(course=course,
                            assignment_id=1620589)
