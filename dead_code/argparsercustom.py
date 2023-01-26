    # TODO alphabetize
    parser.add_argument(
        "-a",
        "-assignment",
        "--assignment",
        dest="assignment",
        default=False,
        action="store_true",
        help="Use this flag to create an assignment",
    )

    parser.add_argument(
        "-all_visible",
        "--all_visible",
        dest="all_visible",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-attendance",
        "--attendance",
        dest="attendance",
        default=False,
        action="store_true",
        help="Take attendance",
    )

    parser.add_argument(
        "-assignment_id",
        "--assignment_id",
        dest="assignment_id",
        help="Assignment ID for no submission",
    )

    parser.add_argument(
        "-c",
        "-course",
        "--course",
        default=None,
        help="INFO course number, e.g. 4604",
    )

    parser.add_argument(
        "-cron",
        "--cron",
        action="store_true",
        help="run maintence jobs",
        dest="cron",
        default=False,
    )

    parser.add_argument(
        "-d",
        "-due",
        "--due",
        help="pass a date in YYYYMMDD for the due date, e.g. 20200824",
    )



    parser.add_argument(
        "-e",
        "-export",
        "--export",
        dest="export",
        help="Export all",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-html",
        action="store_true",
        help="print HTML for semester",
        dest="html",
        default=False,
    )

    parser.add_argument(
        "-n", "-name", "--name", help="the name of the quiz or assignment"
    )

    parser.add_argument(
        "-p", "-points", "--points", dest="points", default=3, type=int
    )

    parser.add_argument(
        "--participation",
        action="store_true",
        help="assigns full points to students who submitted",
        dest="participation",
        default=False,
    )

    parser.add_argument(
        "--publish",
        dest="publish",
        default=False,
        action="store_true",
        help="Use this flag to immediately publish the assignment",
    )

    parser.add_argument(
        "-q",
        "-quiz",
        "--quiz",
        dest="quiz",
        default=False,
        action="store_true",
        help="Use this flag to create a quiz",
    )

    parser.add_argument(
        "-set_extra_time_on_quizzes",
        dest="set_extra_time_on_quizzes",
        default=False,
        action="store_true",
        help="Use this flag to set extra time on all quizzes for students w/ accomodations",
    )

    parser.add_argument(
        "-t",
        "-tomorrow",
        "--tomorrow",
        action="store_true",
        help="syncs a directory to canvas",
        dest="tomorrow",
        default=False,
    )

    parser.add_argument(
        "-tt",
        action="store_true",
        help="syncs a directory to canvas",
        dest="day_after_tomorrow",
        default=False,
    )

    parser.add_argument("-w", "-week", "--week", dest="week", type=int)

    parser.add_argument(
        "-v",
        "-visible",
        "--visible",
        dest="visible",
        default=False,
        action="store_true",
        help="Make html visible",
    )

    parser.add_argument(
        "-z",
        "-zeros",
        "--zeros",
        action="store_true",
        help="assigns zeros to students who have not submitted",
        dest="zeros",
        default=False,
    )
