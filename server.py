import os
import sys
import time
import webbrowser
from flask import Flask, render_template_string
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread
from scripts.utils.inactive.content_loader import load_json_data, validate_data, load_html_template, render_template  # Import content loader functions
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
        # Load and validate the JSON data
        content = load_json_data(content_file_path)
        validate_data(content)

        # Load the HTML template
        template_content = load_html_template(template_file_path)

        # Render the template with the loaded data
        rendered_html = render_template(template_content, content)
        
        return render_template_string(rendered_html)  # Using Flask to serve the rendered content
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        return "An error occurred while rendering the newsletter."

# Watchdog event handler to track file changes
class ReloadHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app

    def on_modified(self, event):
        try:
            if event.src_path == content_file_path or event.src_path == template_file_path:
                with app.app_context():
                    # Reload the template and content
                    logger.info(f'{event.src_path} modified, reloading page...')
                    self.app.jinja_env.cache.clear()
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
