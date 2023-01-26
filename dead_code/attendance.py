from collections import defaultdict
import os
import csv


DIR = "3402"
for fileName in os.listdir(DIR):
    if (fileName != ".ipynb_checkpoints" and "processed" not in fileName):
        print("[*] processing " + fileName)

        date = fileName.split("_")[-1].replace(".csv", "")
        
        attendanceCount = defaultdict(int)

        with open(os.path.join(DIR, fileName), 'r') as currentFile:
            if (fileName.split("_")[0] == "participants"):
                csvReader = csv.reader(currentFile)
                next(csvReader)

                for row in csvReader:
                    minutes = row[-2] # total minutes. Canvas makes 2 rows 
                    if (row[1].find("@") != -1): # has an email
                        attendanceCount[row[0]] += int(minutes)

        fn = DIR + "/processed_" + fileName

        with open(fn, "w") as of:
            of.write("name,present,date,minutes\n")
            for key, value in sorted(attendanceCount.items()):
                #print(key+": "+str(value))
                # write to file
                present = 1 if (value >= 40) else 0
                key = key.replace("'", "").replace(" (They/Them)", "").replace(" (she/her)", "")
                of.write(key + ", " + str(present) + "," + date + "," + str(value) + "\n")



def get_student_attendance(name, folder="3402"):
    """
    Input: a CU email
    Output: a dataframe saying when they were present or not
    Assumes you run py atttendence.py to fill folder (e.g. 3402)

    Matches based on last name lower case. If that is not unique matches on first 3 of first
    This is sufficient for 3402
    """
    name = name.replace("'", "")

    # print(name)

    all_ = pd.concat(pd.read_csv(fn) for fn in glob.glob(folder + "/pro*"))

    # import ipdb;ipdb.set_trace()

    all_["last"] = all_["name"].apply(
        lambda x: x.split()[-1].lower().replace("'", "")
    )
    all_["first3"] = all_["name"].apply(lambda x: x.split()[0].lower()[0:3])

    all_["date"] = all_["date"].apply(lambda x: str(x))

    dates = pd.DataFrame(all_["date"].unique())
    dates.columns = ["date"]

    dates["date"] = dates["date"].apply(
        lambda x: datetime.strptime(str(x), "%Y%m%d")
    )

    dates.sort_values(by="date", inplace=True)

    dates["date"] = dates["date"].apply(
        lambda x: datetime.strftime(x, "%Y%m%d")
    )

    # get student values
    stu = all_[all_["last"] == name.split()[-1].lower()]

    # merge on all dates
    stu = pd.merge(dates, stu, how="outer", on=["date"])

    stu = stu.fillna(0)

    unique_names = [j for j in stu.name.unique().tolist() if type(j) == str]
    if len(unique_names) > 1:

        # additional matching on first 3 chars of first name
        stu = stu[stu["first3"] == name.split()[0].lower()[0:3]]

    stu = stu[["date", "present", "name"]]
    stu["name"] = name

    return stu


if args.attendance:
    # first run $py attendance.py
    course = canvas.get_course(CUnum2canvasnum[args.course])
    roll_call_attendance_no = config["course_info"][
        "roll_call_attendance_no"
    ]

    # read in excused absences
    excused = config["attendance_info"]["excused"]
    excused = defaultdict(lambda: int(config["attendance_info"]["excused"]))

    for alt in config["attendance_info"].keys():
        if alt[0:7] == "student":
            student_no = int(alt.split("_")[1])
            excused[student_no] = int(config["attendance_info"][alt])

    canvasID2email = {}

    for u in course.get_users(enrollment_type=["student"]):
        canvasID2email[u.id] = u.email
        try:
            update_roll_call(
                course=course,
                roll_call_attendance_no=roll_call_attendance_no,
                canvas_student_name=u.name,
                canvas_student_id=u.id,
                excused=excused,
            )
        except AttributeError:
            print("-", "error on student ", u)

    os._exit(0)
