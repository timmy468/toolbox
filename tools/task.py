from PySide6.QtCore import QThread, Signal


class Task(QThread):
    done = Signal(object)
    error = Signal(str)
    progress = Signal(int)
    info = Signal(str)

    def __init__(self, run):
        super().__init__()
        self.fn = run

    def run(self):
        try:
            value = self.fn(
                self.progress.emit,
                self.info.emit,
                self.isInterruptionRequested,
            )
            self.done.emit(value)
        except Exception as error:
            self.error.emit(str(error))
