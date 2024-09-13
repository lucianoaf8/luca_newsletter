import os
import sys
import time
import webbrowser
from flask import Flask, render_template_string
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread
from scripts.utils.content_loader import load_content, render_template  # Import the necessary functions from content_loader
from scripts.utils.logger_config import get_logger  # Your logger config

# Initialize logger
logger = get_logger('server')

app = Flask(__name__)

# Paths for content and template
content_file_path = os.path.join(os.getcwd(), 'data', 'content_feeder', 'content.json')
template_file_path = os.path.join(os.getcwd(), 'templates', 'template.html')

# Serve the page by rendering the template with content data
@app.route('/')
def serve_newsletter():
    try:
        # Load the content from the JSON file
        content = load_content(content_file_path)
        
        # Render the HTML template using the loaded content
        rendered_html = render_template(template_file_path, content)

        # Serve the rendered HTML as a response
        return render_template_string(rendered_html)
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        return "An error occurred while rendering the newsletter."

# Watchdog event handler to track file changes
class ReloadHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app

    def on_modified(self, event):
        try:
            # Reload the template and content if either file changes
            if event.src_path == content_file_path or event.src_path == template_file_path:
                with app.app_context():
                    logger.info(f'{event.src_path} modified, reloading page...')
                    self.app.jinja_env.cache.clear()  # Clear the template cache to reflect changes
        except Exception as e:
            logger.error(f"Error while reloading due to file changes: {e}")

# Start the Flask server in a separate thread
def start_server():
    try:
        # Open the browser after a small delay to ensure the server is running
        time.sleep(1)
        webbrowser.open('http://localhost:5000')
        logger.info("Browser opened at http://localhost:5000")
        app.run(debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Error starting Flask server: {e}")

# Monitor template.html and content.json for changes
def monitor_files():
    try:
        event_handler = ReloadHandler(app)
        observer = Observer()
        
        # Monitor both the content and template directories
        observer.schedule(event_handler, path=os.path.dirname(content_file_path), recursive=False)
        observer.schedule(event_handler, path=os.path.dirname(template_file_path), recursive=False)
        observer.start()
        
        logger.info("Started file monitoring for content and template changes.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    except Exception as e:
        logger.error(f"Error during file monitoring: {e}")

if __name__ == '__main__':
    try:
        # Start Flask server in a separate thread
        server_thread = Thread(target=start_server)
        server_thread.start()

        # Start file monitoring
        monitor_files()
    except Exception as e:
        logger.error(f"Critical error in main execution: {e}")
