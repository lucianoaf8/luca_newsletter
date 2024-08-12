# Email Template Generator - Project Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Project Purpose](#project-purpose)
3. [Technologies Used](#technologies-used)
4. [Project Structure](#project-structure)
5. [Front-end Design and Structure](#front-end-design-and-structure)
6. [Back-end Design and Structure](#back-end-design-and-structure)
7. [Styling](#styling)
8. [Dynamic Content Loading](#dynamic-content-loading)
9. [Development Workflow](#development-workflow)
10. [Future Enhancements](#future-enhancements)

## 1. Introduction

This project is an Email Template Generator that creates a modular, dynamically-loaded HTML email template. It features a "Good Morning" email design with sections for a header, weather widget, and a daily highlight. The project uses a Python-based server for dynamic content loading and live reloading during development.

## 2. Project Purpose

The main goals of this project are:
- To create a modular email template that's easy to maintain and extend
- To implement a development environment that allows for rapid prototyping and instant preview of changes
- To demonstrate best practices in separating concerns between content, structure, and styling
- To provide a flexible system for dynamic content insertion into email templates

## 3. Technologies Used

The project utilizes the following technologies:

- **Front-end**:
  - HTML5
  - CSS3
  - Jinja2 (templating engine)

- **Back-end**:
  - Python 3.x
  - Watchdog (for file system events)
  - Livereload (for browser auto-refresh)
  - SimpleHTTPServer (for serving static files)

- **Data Storage**:
  - JSON (for storing dynamic content)

## 4. Project Structure

The project follows this directory structure:

```
project_root/
│
├── server.py
├── index.html
├── data.json
│
├── css/
│   ├── main.css
│   ├── header.css
│   ├── weather_widget.css
│   └── highlight_section.css
│
├── sections/
│   ├── header.html
│   ├── weather_widget.html
│   └── highlight_section.html
│
├── templates/
│   └── base.html
│
└── assets/
    └── imgs/
        ├── sun-icon.png
        ├── sunrise-icon.png
        └── sunset-icon.png
```

## 5. Front-end Design and Structure

The front-end of the email template is built using HTML5 and CSS3. It's designed to be modular, with each section of the email template separated into its own HTML file.

### 5.1 Base Template (templates/base.html)

The base template serves as the main structure for the email. It includes:
- Meta tags for proper rendering across email clients
- Links to CSS files
- Placeholders for including modular sections
- LiveReload script for development

### 5.2 Modular Sections

Each section of the email is contained in its own HTML file:

1. **Header (sections/header.html)**:
   - Displays the email title and a sun icon
   - Uses dynamic content for the title and icon URL

2. **Weather Widget (sections/weather_widget.html)**:
   - Shows current weather information
   - Includes temperature, min/max temperatures, and sunrise/sunset times
   - Uses dynamic content for all weather data

3. **Highlight Section (sections/highlight_section.html)**:
   - Presents a daily highlight or message
   - Uses dynamic content for the title and message

## 6. Back-end Design and Structure

The back-end is built with Python and serves several purposes:

### 6.1 Server (server.py)

The main server file (server.py) handles:
- Serving static files
- Rendering the HTML template with dynamic content
- Watching for file changes
- Triggering live reloads in the browser

Key components of the server:

1. **EmailTemplateHandler**: A custom HTTP request handler for serving static files.

2. **ChangeHandler**: Watches for file changes and triggers template re-rendering when necessary.

3. **render_template()**: Loads data from JSON and renders the HTML template using Jinja2.

4. **watch_files()**: Sets up a file system observer to detect changes in real-time.

5. **open_browser()**: Automatically opens the default web browser when the server starts.

### 6.2 Data Management

Dynamic content is stored in a JSON file (data.json). This allows for easy updates to the email content without changing the HTML structure.

## 7. Styling

The project uses a modular CSS approach, with styles divided into multiple files:

### 7.1 Main Styles (css/main.css)

Contains:
- General resets
- Common styles for the email container
- Responsive design rules
- Default section styling (including the box shadow effect)

### 7.2 Section-Specific Styles

Each section has its own CSS file:

1. **Header Styles (css/header.css)**:
   - Gradient background
   - Text and icon positioning

2. **Weather Widget Styles (css/weather_widget.css)**:
   - Layout for weather information
   - Styling for temperature, min/max, and sunrise/sunset display

3. **Highlight Section Styles (css/highlight_section.css)**:
   - Background color
   - Text styling for the highlight message

This modular approach allows for easy customization of individual sections without affecting others.

## 8. Dynamic Content Loading

The project uses a JSON file (data.json) to store dynamic content. This content is loaded by the server and injected into the HTML template using Jinja2. This approach allows for easy content updates without changing the HTML structure.

## 9. Development Workflow

The project is set up for an efficient development workflow:

1. The server watches for file changes in HTML, CSS, and JSON files.
2. When a change is detected, the server re-renders the template if necessary.
3. The browser automatically reloads to reflect the changes.
4. Logging is implemented to track file changes and server actions.

This setup allows for rapid prototyping and instant preview of changes.

## 10. Future Enhancements

Possible future enhancements for the project include:

1. Adding more email sections or templates
2. Implementing a GUI for editing the JSON content
3. Adding support for multiple email layouts
4. Integrating with an actual weather API for real-time data
5. Implementing email client-specific optimizations

This modular and flexible structure allows for easy expansion and customization of the email template system.
