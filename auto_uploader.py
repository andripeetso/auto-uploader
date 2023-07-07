#!/usr/bin/env python3
import os
import time
import datetime
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from tqdm import tqdm
import atexit

def notify(title, text):
    applescript = f'display notification "{text}" with title "{title}"'
    subprocess.call(["osascript", "-e", applescript])

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        self.copy_files_from_today()

    def copy_files_from_today(self):
        # Identify the path of the hard drive
        harddrive_path = "/Volumes/NINJAV"

        # Identify the destination folder path
        destination_folder_path = "/Users/andripeetso/Dropbox"

        # Get today's date
        today = datetime.date.today()

        # Get list of all files only in the given directory
        files = [f for f in os.listdir(harddrive_path) if os.path.isfile(os.path.join(harddrive_path, f))]

        # Filter out macOS's "._" hidden files and only take files from today
        files = [f for f in files if not f.startswith("._") and datetime.date.fromtimestamp(os.path.getmtime(os.path.join(harddrive_path, f))) == today]

        # If there are files from today
        if files:
            for file in files:
                # Copy the file to the destination folder
                print(f"Starting to copy the file {file}")
                self.copyfile_progress(os.path.join(harddrive_path, file), os.path.join(destination_folder_path, file))
                print(f"File {file} copied to {destination_folder_path}")
                notify("File Copied", f"File {file} copied to {destination_folder_path}")

    # Function to copy file with progress bar
    def copyfile_progress(self, src, dst):
        total = os.path.getsize(src)
        with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst, tqdm(total=total, unit='B', unit_scale=True, desc=dst) as pbar:
            for buf in iter(lambda: fsrc.read(1024*1024), b''):  # 1MB chunks
                fdst.write(buf)
                pbar.update(len(buf))

def is_drive_connected(path):
    return os.path.exists(path)

# Set observer to watch for changes in the hard drive directory
if __name__ == "__main__":
    drive_path = "/Volumes/NINJAV"

    if not is_drive_connected(drive_path):
        print(f"Drive not connected at path: {drive_path}")
        exit(1)

    print("Drive connected. Setting up file observer...")
    event_handler = MyHandler()
    event_handler.copy_files_from_today()
    observer = Observer()
    observer.schedule(event_handler, path=drive_path, recursive=False)
    observer.start()

    # Make sure the observer is stopped when the script exits.
    atexit.register(observer.stop)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
