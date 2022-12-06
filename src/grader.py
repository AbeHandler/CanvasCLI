from src.api import get_api
from src.config import Config
from canvasapi.course import Course
from pathlib import Path


class Grader(object):

	def __init__(self, course: Course):
		self.course = course 


	def download_all_submitted_files_with_extension(self,
													assignment_id: str = "1533042",
	                                                extension: str = ".py",
	                                                download_base_directory: Path = Path("/tmp")
	                                                ):
	    '''
	    Downloads all files with a given extension to download_base_directory/assignment_id
	    '''
	    assignment = course.get_assignment(assignment_id)
	    base_directory: Path = download_base_directory / assignment_id
	    
	    for submission in assignment.get_submissions():
	        for attachment in submission.attachments:
	            file_name = attachment.filename
	            if file_name.endswith(extension):
	                
	                save_subdir = base_directory / str(submission.user_id)
	                save_subdir.mkdir(parents=True, exist_ok=True)
	                
	                save_here = save_subdir / file_name 
	                attachment.download(save_here.as_posix())
	                print(f"[*] Downloaded {save_here.as_posix()}")
        

if __name__ == "__main__":
	api = get_api()
	config = Config(Path("/Users/abe/CanvasCLI/3220S2023.ini"))
	course = api.get_course(config.canvas_no)
	grader = Grader(course)
	grader.download_all_submitted_files_with_extension(extension="png")
