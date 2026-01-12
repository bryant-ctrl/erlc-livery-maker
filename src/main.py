"""
ER:LC Livery Maker - Main Entry Point
"""
import sys
from PyQt6.QtWidgets import QApplication
from livery_generator_window import LiveryGeneratorWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("ER:LC Livery Maker")

    window = LiveryGeneratorWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
