import sys
from PyQt6.QtWidgets import QApplication
from view import MainWindow
from presenter import Presenter


def main():
	app = QApplication(sys.argv)
	view = MainWindow()
	presenter = Presenter(view)
	view.show()
	sys.exit(app.exec())


if __name__ == "__main__":
	main()
