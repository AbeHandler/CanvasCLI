

class Assignment(object):

    def __init__(self, config: Config, api: Canvas):
        self.config = config
        self.course = api.get_course(config.canvas_no)