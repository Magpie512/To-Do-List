# Advanced To-Do List

A modern, comfortable, and feature-rich To-Do List application built with Python and Tkinter. It helps you manage your daily tasks, set priorities, and keep track of deadlines with an easy-to-use interface.

## Features

- **Modern UI:** A clean, easy-on-the-eyes interface with a comfortable color palette and alternating row colors for readability.
- **Smart Sorting:** Click on any column header (Task Title, Importance, Deadline, Status) to quickly sort your tasks. Click again to reverse the order.
- **Priority Management:** Assign tasks as Low, Medium, or High priority.
- **Calendar Integration:** Pick deadlines effortlessly using the built-in calendar widget (`tkcalendar`).
- **Quick Actions:** Double-click on any task in the list to quickly toggle its completion status. 
- **Auto-Save:** Tasks are automatically saved to your local Windows `AppData` directory (`%APPDATA%\AdvancedTodoList`), so you never lose your progress between sessions.

## Running from Source

To run the application directly using Python, you'll need to install the required dependencies first.

1. **Install Dependencies:**
   Make sure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: The main external dependency is `tkcalendar`)*

2. **Run the App:**
   ```bash
   python TODOapp.py
   ```

## Building the Executable (.exe)

If you want to share the application or run it without needing Python installed, you can bundle it into a standalone executable using `PyInstaller`. A specification file (`TODOapp.spec`) is already provided for you.

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Build the App:**
   Run the following command in the root directory of the project:
   ```bash
   pyinstaller TODOapp.spec --clean -y
   ```

3. **Locate the `.exe`:**
   Once the build process completes, your standalone executable will be located in the `dist` folder:
   `dist/TODOapp.exe`

You can move this `.exe` file anywhere on your computer or send it to others, and it will run independently!
