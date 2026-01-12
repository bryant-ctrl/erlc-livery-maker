"""
ER:LC Livery Maker - Main Entry Point (Tkinter version)
"""
import sys
import tkinter as tk
from livery_generator_window_tk import LiveryGeneratorApp


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = LiveryGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
