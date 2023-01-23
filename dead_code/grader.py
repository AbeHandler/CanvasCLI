from src.api import get_api
from src.config import Config
from canvasapi.course import Course
from pathlib import Path


class Grader(object):

    def __init__(self, course: Course):
        self.course = course 


    def download_all_submissions_for_assigment(self,
                                               assignment_id: str = "1533042",
                                               extension: str = ".py",
                                               download_base_directory: Path = Path("/tmp")
                                               ):
        '''
        Downloads all files with a given extension to download_base_directory/assignment_id
        '''
        assignment = course.get_assignment(assignment_id)

        local_download_location: Path = download_base_directory / assignment_id
        
        for submission in assignment.get_submissions():
            for attachment in self._attachments_with_extension(submission.attachments, extension):
                    
                    save_here = self._get_local_path(download_base_directory = download_base_directory,
                                                     assignment_id = str(assignment_id),
                                                     user_id = str(submission.user_id),
                                                     file_name = str(attachment.filename))
                    attachment.download(save_here.as_posix())
                    print(f"[*] Downloaded {save_here.as_posix()}")
        
    def _attachments_with_extension(self, attachments, extension):
        return [attachment for attachment in attachments if attachment.filename.endswith(extension)]

    def _get_local_directory(self,
                             download_base_directory: Path,
                             assignment_id: str,
                             user_id: str) -> Path:
        save_here = download_base_directory / assignment_id / user_id
        save_here.mkdir(parents=True, exist_ok=True)
        return save_here

    def _get_local_path(self,
                        download_base_directory: Path,
                        assignment_id: str,
                        user_id: str,
                        file_name: str) -> Path:
        
        local_dir = self._get_local_directory(download_base_directory, assignment_id, user_id)
        return local_dir / file_name

if __name__ == "__main__":
    api = get_api()
    config = Config(Path("/Users/abe/CanvasCLI/3220S2023.ini"))
    course = api.get_course(config.canvas_no)
    grader = Grader(course)
    grader.download_all_submissions_for_assigment(extension="png")
