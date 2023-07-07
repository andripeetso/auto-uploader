import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import threading
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import datetime
import queue

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app

    def on_modified(self, event):
        self.app.start_copying()

class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Auto Uploader")
        self.destination_folder = None
        self.create_widgets()
        self.queue = queue.Queue()
        self.copy_thread = None

    def create_widgets(self):
        # Create select destination folder button
        self.select_button = tk.Button(self, text="Select Destination", command=self.select_destination_folder)
        self.select_button.pack()

        # Create start copying button
        self.start_button = tk.Button(self, text="Start Copying", command=self.start_copying, state=tk.DISABLED)
        self.start_button.pack()

        # Create destination folder label
        self.destination_label = tk.Label(self, text="No destination selected.")
        self.destination_label.pack()

        # Create progress bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress.pack()

        # Create status label
        self.status_label = tk.Label(self, text="Idle.")
        self.status_label.pack()

    def select_destination_folder(self):
        # Open folder selection dialog
        folder = filedialog.askdirectory()
        if folder:
            self.destination_folder = folder
            self.destination_label.config(text=f"Destination: {folder}")
            if not self.copy_thread or not self.copy_thread.is_alive():
                self.start_button.config(state=tk.NORMAL)  # Enable start copying button only if no copy is in progress

    def start_copying(self):
        # Disable start copying button
        self.start_button.config(state=tk.DISABLED)

        # Start file copying in a separate thread
        self.copy_thread = threading.Thread(target=self.copy_files_from_today)
        self.copy_thread.start()
        self.check_queue()

    def copy_files_from_today(self):
        # Identify the path of the hard drive
        harddrive_path = "/Volumes/NINJAV"

        # Get list of all files only in the given directory
        files = [f for f in os.listdir(harddrive_path) if os.path.isfile(os.path.join(harddrive_path, f))]

        # Get today's date
        today = datetime.date.today()

        # Filter files modified today
        files_today = [f for f in files if datetime.date.fromtimestamp(os.path.getmtime(os.path.join(harddrive_path, f))) == today]

        # If there are files modified today
        if files_today:
            for file in files_today:
                # Copy the file to the destination folder
                self.copyfile_progress(os.path.join(harddrive_path, file), os.path.join(self.destination_folder, file))
        self.queue.put(None)

    def copyfile_progress(self, src, dst):
        # Get total size of source file
        total = os.path.getsize(src)

        # Open source file and destination file
        with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
            copied = 0

            # Copy source file to destination file chunk by chunk
            while True:
                buf = fsrc.read(1024*1024)  # 1MB chunks
                if not buf:
                    break
                fdst.write(buf)
                copied += len(buf)

                # Update progress bar and status label
                self.progress["value"] = copied / total * 100
                self.status_label.config(text=f"Copying {os.path.basename(src)}: {copied / total * 100:.2f}%")

        self.status_label.config(text=f"{os.path.basename(src)} copied to {self.destination_folder}.")

    def check_queue(self):
        try:
            msg = self.queue.get(0)
            # Enable start copying button only if the copy_thread is not active
            if self.copy_thread and not self.copy_thread.is_alive():
                self.start_button.config(state=tk.NORMAL)
        except queue.Empty:
            self.after(100, self.check_queue)

if __name__ == "__main__":
    app = Application()
    app.mainloop()
