import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ImageHandler(FileSystemEventHandler):
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.feh_process = None

    def start_feh_slideshow(self):
        if self.feh_process:
            self.feh_process.terminate()
        
        self.feh_process = subprocess.popen(["feh", "-F", "-Y", "-D", "300", self.folder_path],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        print("Slideshow iniciado con feh.")
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            filename = os.path.basename(event.src_path)
            print(f'Nuevo archivo detectado: {filename}')
            self.start_feh_slideshow()

def monitor_folder(folder_path):
    event_handler = ImageHandler(folder_path)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    print(f'Monitorizando la carpeta: {folder_path}')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.feh_process:
            event_handler.feh_process.terminate()
    observer.join()

if __name__ == "__main__":
    folder_to_watch = 'static/uploads'
    monitor_folder(folder_to_watch)