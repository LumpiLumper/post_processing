
import sys
from PyQt6.QtWidgets import QApplication
from scripts.ui import FluentProcessingUI

from scripts.gui_v2 import MainWindow

app = QApplication(sys.argv)
main_window = MainWindow()

app.exec()