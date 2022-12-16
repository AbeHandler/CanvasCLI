'''Code related to quizzes goes here'''

def create_quiz(due, tomorrow, course, publish=False, points=3):
    if due is None and tomorrow is None:
        print("[*] You must set a due date")
        os._exit(0)
    if due is None and tomorrow is not None:
        due = get_tomorrow()
    classtime = CUno2Classtime[course]
    course = canvas.get_course(CUnum2canvasnum[course])
    title = datetime.strptime(due, "%Y%m%d").strftime("%b. %d") + " Quiz"

    course.create_quiz(
        {
            "title": title,
            "published": publish,
            "time_limit": 5,
            "allowed_attempts": 2,
            "scoring_policy": "keep_average",
            "points_possible": points,
            "due_at": due + "T" + classtime,
        }
    )
    print("[*] created quiz for {}".format(course))
    os._exit(0)

def set_extra_time_on_quizzes(
    course, names, names2ids_course, extra_minutes=10
):
    """
    course = canvas.get_course(CUnum2canvasnum["3401"])
    names = [o.replace('\n', "") for o in open("accomodations3401.txt")]
    names2ids_course = names2ids["3401"]

    To see this in the Canvas UI click "Moderate this quiz"
    https://community.canvaslms.com/t5/Instructor-Guide/Once-I-publish-a-quiz-how-can-I-give-my-students-extra-attempts/ta-p/1242
    $ canvas -set_extra_time_on_quizzes -c 3401
    """
    ids = [names2ids_course[i] for i in names]

    for quiz in course.get_quizzes():
        print("[*] Setting accomodation for {}".format(quiz.title))
        for id_ in ids:
            print("-", id_)
            quiz.set_extensions([{"user_id": id_, "extra_time": extra_minutes}])