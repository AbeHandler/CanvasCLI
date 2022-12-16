
def update_roll_call(
    course,
    roll_call_attendance_no,
    canvas_student_name,
    canvas_student_id,
    excused,
):
    """
    - Canvas has a built in roll call attendance feature
    - Each student automatically is submitted to roll call attendance
    - Write their history to your_attendance.csv and upload to justify attendance
    """

    # print(canvas_student_name)
    attendance_csv = get_student_attendance(canvas_student_name)
    assignment = course.get_assignment(assignment=roll_call_attendance_no)
    submission = assignment.get_submission(canvas_student_id)  # student id

    # 5 free excused absences
    score = (sum(attendance_csv["present"]) + excused[canvas_student_id]) / len(
        attendance_csv["present"]
    )

    score = 1.0 if score > 1.0 else score

    print(canvas_student_name, score * 100)

    submission.edit(
        submission={"posted_grade": int(score * 100)}, comment={"present"}
    )

    """
    Not used
    attendance_csv.to_csv("your_attendance.csv", index=False)
    try:
        submission.edit(submission={'posted_grade': int(score * 100)}, comment={'present'})
        # write student's attendance history to a csv called history.csv
        submission.upload_comment("your_attendance.csv") # reference
    except CanvasException:
        print("error on {}".format(canvas_student_name))
    """
