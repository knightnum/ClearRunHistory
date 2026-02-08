import tkinter as tk
from tkinter import messagebox, ttk
import winreg
import ctypes
import sys
import os

# Function to get the correct path for resources (like icons) 
# both in development and after being bundled into an .exe
def resource_path(relative_path):
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Registry path where Windows stores 'Run' command history
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU"

class ClearRunHistory:
    def __init__(self, root):
        self.root = root
        self.root.title("ClearRunHistory")
        self.root.geometry("450x580")
        self.root.resizable(False, False)
        
        # --- Icon Management Section ---
        icon_name = "app_icon.ico"
        self.icon_path = resource_path(icon_name)
        try:
            # Set AppUserModelID to ensure the icon appears correctly on the taskbar
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("knightnum.runclean.v1")
            if os.path.exists(self.icon_path):
                self.root.iconbitmap(self.icon_path)
        except:
            # Silent fail if icon setup fails
            pass

        self.all_selected = False
        self.checkboxes = []

        # Initialize the User Interface
        self._setup_ui()
        
        # Load registry history after a short delay to ensure UI is ready
        self.root.after(100, self.load_history)

    def _setup_ui(self):
        # Apply Windows-style theme for a classic look
        self.style = ttk.Style()
        try:
            self.style.theme_use('vista')
        except:
            self.style.theme_use('winnative')

        # Header Label
        tk.Label(self.root, text="Run Command History", font=("Tahoma", 11, "bold"), pady=15).pack()

        # --- List Area Container ---
        self.container = tk.Frame(self.root, bd=2, relief="sunken")
        self.container.pack(fill=tk.BOTH, expand=True, padx=20)

        # Canvas for scrollable content
        self.canvas = tk.Canvas(self.container, bg="white", highlightthickness=0)
        # Visible Vertical Scrollbar
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        # Update scrollregion whenever the inner frame size changes
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Place the inner frame inside the canvas
        self.scroll_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Adjust the inner frame width to match the canvas width
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.scroll_window, width=e.width))
        
        # Enable mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # --- Control Buttons Area ---
        self.footer = tk.Frame(self.root, pady=15)
        self.footer.pack(fill=tk.X)

        self.btn_select_toggle = ttk.Button(self.footer, text="Select All", command=self.toggle_select)
        self.btn_select_toggle.pack(side=tk.LEFT, padx=30)

        self.btn_refresh = ttk.Button(self.footer, text="Refresh", command=self.load_history)
        self.btn_refresh.pack(side=tk.RIGHT, padx=30)

        self.btn_delete = ttk.Button(self.root, text="DELETE SELECTED", command=self.delete_selected)
        self.btn_delete.pack(fill=tk.X, padx=30, pady=(0, 10))

        # Copyright Footer
        tk.Label(self.root, text="Copyright © 2025 Knightnum Limited. All rights reserved.", 
                 font=("Tahoma", 7), fg="#888888", pady=10).pack(side=tk.BOTTOM)

    def _on_mousewheel(self, event):
        # Handle scroll direction based on mouse wheel delta
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def load_history(self):
        """Fetch history items from Windows Registry and generate checkboxes."""
        # Clear existing items in the list
        for cb in self.checkboxes:
            cb.destroy()
        self.checkboxes = []
        
        try:
            # Open the registry key with Read access
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    # 'MRUList' is a system key used for sorting, skip it
                    if name != "MRUList":
                        # Strip trailing '\1' indicator used by Windows Registry
                        # slice [:-2] ensures numbers like '1' in IP addresses are not removed
                        clean_val = value[:-2] if value.endswith('\\1') else value
                        
                        var = tk.BooleanVar()
                        # Create Checkbutton for each command found
                        cb = tk.Checkbutton(self.scrollable_frame, text=clean_val, variable=var,
                                          bg="white", font=("Tahoma", 9), anchor="w", justify="left")
                        cb.var = var
                        cb.reg_name = name
                        cb.pack(fill=tk.X, padx=10, pady=1)
                        self.checkboxes.append(cb)
                    i += 1
                except OSError:
                    # End of registry enumeration
                    break
            winreg.CloseKey(key)
        except:
            # General registry access failure
            pass
            
        # Refresh UI layout to recalculate scrollbar position
        self.root.update_idletasks()

    def toggle_select(self):
        """Toggles between Select All and Deselect All based on current state."""
        self.all_selected = not self.all_selected
        for cb in self.checkboxes:
            cb.var.set(self.all_selected)
        # Update button text to reflect the next possible action
        self.btn_select_toggle.config(text="Deselect All" if self.all_selected else "Select All")

    def delete_selected(self):
        """Deletes the selected registry values after user confirmation."""
        to_delete = [cb for cb in self.checkboxes if cb.var.get()]
        if not to_delete:
            messagebox.showwarning("Warning", "Please select at least one item to delete.")
            return

        if messagebox.askyesno("Confirm", f"Are you sure you want to delete {len(to_delete)} items?"):
            try:
                # Re-open key with All Access permissions for deletion
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_ALL_ACCESS)
                for cb in to_delete:
                    winreg.DeleteValue(key, cb.reg_name)
                winreg.CloseKey(key)
                
                # Refresh the list to reflect changes
                self.load_history()
                messagebox.showinfo("Success", "Selected items have been removed from history.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete items: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClearRunHistory(root)
    root.mainloop()