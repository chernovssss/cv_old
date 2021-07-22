from mainwindow import MainWindow


class DataSingleton:
    def __init__(self):
        self.current_instrument = None
        self.action_inst_dict = {}
        self.action_filter_dict = {}

        self.pen_size = 2

        # TODO Do colors
        # self.primary_color = QColor(Qt.black)
        # self.secondary_color = QColor(Qt.white)

        self.UNTITLED = 'Untitled'
        self.PROGRAM_NAME = 'fake-painter'

        self.disabled_plugin_names = []

        self.plugins = {}

        self.disabled_plugins = {}

        self.image = DataSingleton.Image()

        self.mainWindow = MainWindow(self)

    class Image:
        def __init__(self):
            self.history_depth = 40
            self.base_width = 640
            self.base_height = 480



instance = DataSingleton()
