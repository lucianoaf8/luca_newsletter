# Daily Newsletter Email Template

## Overview

This project is a dynamic, visually appealing daily newsletter email template designed to deliver engaging content to users. The newsletter is driven by a `data.json` file, which allows for easy updates and customization without altering the core HTML structure. The template includes sections for weather highlights, finance information, and potentially other engaging content, all designed to be cohesive, modern, and static for compatibility with various email clients.

## Features

- **Dynamic Content:** All content is pulled from a `data.json` file, making it easy to update and maintain.
- **Modular Design:** The template is divided into separate, reusable components, making it easy to add, remove, or modify sections.
- **Responsive Layout:** While primarily designed for static viewing in emails, the layout is optimized for readability on both desktop and mobile devices.
- **Static Design:** The template avoids complex interactivity to ensure compatibility across all email clients.

## Project Structure

The project is organized into a clear and logical directory structure, ensuring that files are easy to find and manage:

### Root Directory

- **index.html:** The main HTML file that serves as the entry point for the newsletter.
- **data.json:** The file that contains all dynamic content for the newsletter.
- [**server.py](http://server.py/):** The backend script for local development and testing.
- **.gitignore:** Specifies files and directories that Git should ignore.
- [**project-documentation.md](http://project-documentation.md/):** Contains in-depth documentation about the project design thinking and goals.
- [**README.md](http://readme.md/):** This file, providing an overview of the project.
- **technical_documentation.md:** Contains technical guidelines and details for the project.

### /assets/imgs

- Contains various icon and image files used throughout the newsletter.

### /css

- Contains CSS files for different sections of the newsletter, including:
    - **finance_highlights.css**
    - **footer.css**
    - **fun_fact.css**
    - **header.css**
    - **highlight_section.css**
    - **main.css**
    - **motivational_gif.css**
    - **motivational_quote.css**
    - **news.css**
    - **weather_widget.css**

### /sections

- Contains HTML files for different sections of the newsletter, including:
    - **finance_highlights.html**
    - **footer.html**
    - **fun_fact.html**
    - **header.html**
    - **highlight_section.html**
    - **motivational_gif.html**
    - **motivational_quote.html**
    - **news.html**
    - **weather_widget.html**

### /templates

- **base.html:** The base template file that includes the main structure of the newsletter, with placeholders for sections to be included dynamically.

## Installation

To set up the project locally:

1. Clone the repository to your local machine:
    
    ```bash
    git clone <https://github.com/yourusername/newsletter-template.git>
    
    ```
    
2. Navigate to the project directory:
    
    ```bash
    cd newsletter-template
    
    ```
    
3. Install the required dependencies:
    
    ```bash
    pip install -r requirements.txt
    
    ```
    
4. Run the local development server:
    
    ```bash
    python server.py
    
    ```
    
5. Open your web browser and navigate to `http://localhost:8000` to view the newsletter.

## Usage

- **Updating Content:** All dynamic content is stored in the `data.json` file. Modify this file to update the text, images, links, and other content displayed in the newsletter.
- **Adding New Sections:** To add a new section, create a new HTML file in the `/sections` directory, update the `data.json` with the relevant content, and include the new section in `base.html`.
- **Styling:** Modify or add CSS in the `/css` directory to change the appearance of the newsletter. Ensure that any new styles are compatible with email clients.

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bug fix:
    
    ```bash
    git checkout -b feature/new-section
    
    ```
    
3. Commit your changes:
    
    ```bash
    git commit -m "Add new feature"
    
    ```
    
4. Push to the branch:
    
    ```bash
    git push origin feature/new-section
    
    ```
    
5. Create a Pull Request.

## Guidelines for Development

- **Maintain Consistency:** Follow the existing design language, including typography, color schemes, and layout principles.
- **Content-Driven:** Ensure all content is sourced from the `data.json` file for easy updates and maintenance.
- **Test Across Clients:** Test any changes in multiple email clients to ensure compatibility and readability.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact

For any inquiries or support, please contact [your-email@example.com](mailto:your-email@example.com).