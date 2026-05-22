@echo off
echo Building Advanced To-Do List...
pyinstaller TODOapp.spec --clean -y
echo.
echo Build complete! You can find the executable in the "dist" folder.
pause
