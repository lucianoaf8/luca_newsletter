import json
import logging
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from jinja2 import Environment, FileSystemLoader
from livereload import Server

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EmailTemplateHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

def load_data():
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("data.json file not found")
        return {}
    except json.JSONDecodeError:
        logging.error("Error decoding data.json")
        return {}

def render_template():
    try:
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('templates/base.html')
        data = load_data()
        
        with open('index.html', 'w') as f:
            f.write(template.render(data=data))
        logging.info("index.html rendered successfully")
    except Exception as e:
        logging.error(f"Error rendering template: {str(e)}")

class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = {}

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(('.html', '.css', '.json')):
            current_time = time.time()
            if event.src_path not in self.last_modified or current_time - self.last_modified[event.src_path] > 1:
                self.last_modified[event.src_path] = current_time
                logging.info(f"File {event.src_path} has been changed")
                if event.src_path.endswith(('.html', '.json')):
                    render_template()

def watch_files():
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def open_browser():
    webbrowser.open('http://localhost:8000')

if __name__ == '__main__':
    render_template()
    
    # Set up livereload server
    server = Server()
    server.watch('index.html')
    server.watch('css/')
    server.watch('sections/')
    server.watch('data.json')
    
    # Start file watcher in a separate thread
    import threading
    watcher_thread = threading.Thread(target=watch_files)
    watcher_thread.start()
    
    # Open the browser after a short delay
    threading.Timer(1.0, open_browser).start()
    
    # Serve the application
    logging.info("Starting server at http://localhost:8000")
    server.serve(root='.', port=8000, host='localhost')