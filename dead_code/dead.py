def get_week_folder(course_no, week_no):
    '''Get the folder for a given week'''
    course = canvas.get_course(CUno2canvasno[args.course])
    for f in course.get_folders():
        if f.name == "week{}".format(args.week):
            return f


def get_folder_for_week(week, course, folder_kind='whiteboards'):
    '''
    Get the Canvas folder for whiteboards for some week
    e.g. files/week16/whiteboards
    '''
    course = canvas.get_course(CUno2canvasno[course])
    for f in course.get_folders():
        folder_name = f.full_name.split(' ').pop()
        if folder_name == "files/week{}/{}".format(week, folder_kind):
            return f
    return None    if args.html:

        # show  before date
        course = canvas.get_course(CUno2canvasno[args.course])

        lecture_page = course.get_page(args.course)

        html = BeautifulSoup(lecture_page.body, features="html.parser")

        for li in html.findAll("li"):

            try:
                week = dates2weeks[li.attrs["data-date"]]

                folder_kind = "in-class-code"

                if args.week is None:
                    print("You must specify a week")
                    os._exit(0)

                if week == args.week:

                    if li.attrs["data-bullet"] == folder_kind:
                        folder = get_folder_for_week(
                            week, args.course, folder_kind=folder_kind)
                        if folder is not None:
                            for file in folder.get_files():
                                if li["data-date"] in file.display_name:

                                    url = file.url.split("/download")[0]
                                    link = make_link(link_text=folder_kind,
                                                     href=url,
                                                     title=file.display_name)

                                    ll = BeautifulSoup(
                                        link, features="html.parser")
                                    print("inserting")

                                    li.string = ""  # remove inner text
                                    li.insert(0, ll)
                                    lecture_page.edit(
                                        wiki_page={"body": str(html)})
                                    os._exit(0)
            except KeyError:
                pass

        os._exit(0)    if args.sync and args.week is None:
        print("[*] you must scecify a week with sync")

    if args.sync and args.week is not None:

        # $ canvas -w 3 -sync -c 2301

        folder = get_week_folder(CUno2canvasno[args.course], args.week)

        for subfolder in folder.get_folders():
            name = subfolder.name
            glb = os.environ["ROOT"] + "/everything/teaching/{}{}/week{}/{}/*".format(
                args.course, SEMESTER, args.week, name)
            already_uploaded = [j.display_name for j in subfolder.get_files()]

            for fn in glob.glob(glb):
                fname = fn.split("/").pop()
                if fn.split("/").pop() not in already_uploaded:
                    print("- uploading {} to {}".format(fname, subfolder))
                    subfolder.upload(fn, on_duplicate="overwrite")