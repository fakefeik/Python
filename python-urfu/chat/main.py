"""
Main entry point for the application
"""

from PyQt5 import QtWidgets
import graphics


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    scr = graphics.InfoWindow()
    scr.show()
    exit(app.exec_())
