'''

There seem to be discrepancies between the nbgrader feedback file 
and the autograded scores in the gradebook.

Let's use the feedback file as the source of truth

'''
from pathlib import Path
from bs4 import BeautifulSoup


class Feedback(object):

    def __str__(self):
        return self.file.as_posix()

    def __init__(self, 
                 file: Path):
        self.file = file
        with open(file.as_posix(), "r") as inf:
            html_doc = inf.read()

        soup = BeautifulSoup(html_doc, 'html.parser')

        toc = soup.find("div", {"id": "toc"})

        total = 0

        for _ in toc.find_all("li"):
            awarded, possible = _.text.split(":").pop().rstrip(")").split("/")
            awarded = float(awarded.strip())
            total += awarded

        self.score = total