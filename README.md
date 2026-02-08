# ClearRunHistory

ClearRunHistory is a lightweight Windows utility built with Python and Tkinter. It allows users to view, manage, and selectively clear the command history from the Windows "Run" dialog (Win + R).

## Features
- **Native Look & Feel:** Uses the `vista` theme for a classic Windows GUI experience.
- **Smart History Retrieval:** Fetches real-time data from the Windows Registry (`RunMRU`).
- **Selective Deletion:** Toggle "Select All" or choose specific items to remove.
- **Fixed String Logic:** Properly handles IP addresses and network paths without corrupting the text.
- **Built-in Scroll Support:** Seamlessly navigate long lists of history items using the mouse wheel.
- **Taskbar & Titlebar Support:** Includes custom icon integration for professional deployment.

## Prerequisites
- Windows OS (10/11)
- Python 3.x
- `pyinstaller` (for building the .exe)

## Compilation
To create a standalone executable, ensure you have an `app_icon.ico` in the root folder, then run:

```bash
pyinstaller --noconsole --onefile --icon=app_icon.ico --add-data "app_icon.ico;." --name ClearRunHistory ClearRunHistory.py
