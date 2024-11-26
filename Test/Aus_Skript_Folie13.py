
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, Slot

class Communicate(QObject):
    speak = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.speak[str].connect(self.say_something)

    # define a new slot
    @Slot(str)
    def say_something(self, arg):
        print("This is a string:", arg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    someone = Communicate()
    someone.speak.emit("Hello everybody!")
