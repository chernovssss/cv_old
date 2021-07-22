class DataSingleton:
    def __init__(self):
        self.closing_value = 5
        self.dilation_value = 3
        self.blur_value = 3

    def set_closing(self, value):
        self.closing_value = value

    def set_dilation(self, value):
        self.dilation_value = value

    def set_blur(self, value):
        self.blur_value = value


instance = DataSingleton()
