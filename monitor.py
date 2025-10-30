import time
import os
import subprocess
import signal
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# variables globales para que el handler de señales pueda acceder
current_handler = None
current_observer = None

class ImageHandler(FileSystemEventHandler):
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.feh_process = None

    def start_feh_slideshow(self):
        if self.feh_process:
            self.feh_process.terminate()
        
        # Usar --auto-zoom (-Z) para ajustar la imagen al marco respetando la relación de aspecto,
        # y -B black para que las bandas laterales queden negras en vez de rellenar.
        self.feh_process = subprocess.Popen(
            ["feh", "-F", "-Z", "-B", "black", "-D", "300", self.folder_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("Slideshow iniciado con feh.")
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            filename = os.path.basename(event.src_path)
            print(f'Nuevo archivo detectado: {filename}')
            self.start_feh_slideshow()

def _signal_handler(signum, frame):
    print(f"Recibida señal {signum}, cerrando feh y observador...")
    if current_handler and getattr(current_handler, 'feh_process', None):
        try:
            current_handler.feh_process.terminate()
        except Exception:
            pass
    if current_observer:
        try:
            current_observer.stop()
        except Exception:
            pass
    sys.exit(0)

def monitor_folder(folder_path):
    global current_handler, current_observer
    event_handler = ImageHandler(folder_path)
    current_handler = event_handler
    observer = Observer()
    current_observer = observer
    observer.schedule(event_handler, folder_path, recursive=False)

    # registrar manejadores de señal para terminar correctamente
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

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