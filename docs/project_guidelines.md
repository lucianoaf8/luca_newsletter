# New Sections and Changes Guidelines

This document provides guidelines for developers who want to add new sections or make changes to the existing Luca Newsletter project. Following these guidelines will ensure that additions and modifications are consistent with the current design and functionality.

## Adding a New Section

### 1. Create HTML Template

1. Navigate to the `src/sections/` directory.
2. Create a new HTML file for your section, using kebab-case naming convention (e.g., `new-section.html`).
3. Use Jinja2 templating syntax for dynamic content.
4. Follow the existing pattern for section structure:

```html
<div class="section new-section">
    <h2>{{ data.new_section.title }}</h2>
    <!-- Add your section content here -->
</div>
```

### 2. Create CSS File

1. Navigate to the `src/css/` directory.
2. Create a new CSS file with the same name as your HTML file (e.g., `new-section.css`).
3. Use the existing naming conventions and follow the established CSS patterns:

```css
.new-section {
    padding: 20px;
    background-color: #f0f0f0;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    margin-top: 20px;
}

.new-section h2 {
    font-family: var(--secondary-font);
    font-size: 28px;
    color: #2c3e50;
    margin-bottom: 15px;
}

/* Add more styles as needed */
```

### 3. Update `main.css`

1. Open `src/css/main.css`.
2. Import your new CSS file at the end of the existing imports:

```css
@import 'new-section.css';
```

### 4. Update `base.html`

1. Open `src/templates/base.html`.
2. Add your new section to the appropriate place in the template:

```html
{% include 'sections/new-section.html' %}
```

### 5. Update `data.json`

1. Open `data.json` in the root directory.
2. Add a new object for your section's data:

```json
{
    "new_section": {
        "title": "New Section Title",
        "content": "New section content"
        // Add more fields as needed
    }
}
```

## Modifying Existing Sections

### 1. HTML Changes

1. Locate the relevant section file in `src/sections/`.
2. Make your changes, ensuring you maintain the existing structure and Jinja2 syntax.
3. If adding new dynamic content, make sure to update `data.json` accordingly.

### 2. CSS Changes

1. Find the corresponding CSS file in `src/css/`.
2. Make your style changes, following the existing patterns and naming conventions.
3. Use variables from `main.css` where applicable (e.g., `var(--primary-font)`).
4. Ensure your changes are responsive by adding media queries if necessary.

### 3. JavaScript Changes (if applicable)

1. If adding new interactive features, create a new JS file in a `src/js/` directory (you may need to create this directory).
2. Import your JS file in `base.html` before the closing `</body>` tag.
3. Update `server.py` to include the new JS file in the build process.

## Best Practices

1. **Consistency**: Maintain consistent naming conventions, coding style, and design patterns.
2. **Modularity**: Keep sections self-contained to make the newsletter easy to maintain and customize.
3. **Responsiveness**: Ensure all new content and styles work well on various screen sizes.
4. **Accessibility**: Use semantic HTML and maintain good color contrast for readability.
5. **Performance**: Optimize images and minimize CSS/JS to keep the newsletter lightweight.
6. **Testing**: Test your changes in various email clients to ensure compatibility.

## Integration with Build Process

1. After making changes, run the development server using `python server.py`.
2. The server will automatically detect your changes and rebuild the newsletter.
3. Check the console for any error messages during the build process.
4. Verify your changes in the browser at `http://localhost:8000`.

## Version Control

1. Create a new branch for your changes: `git checkout -b feature/new-section`.
2. Make your changes and commit them with clear, descriptive commit messages.
3. Push your branch and create a pull request for review before merging into the main branch.

## Documentation

1. Update any relevant documentation to reflect your changes or additions.
2. If adding new functionality, consider updating the README.md file.

By following these guidelines, you'll ensure that new sections and changes to the Luca Newsletter project maintain consistency with the existing design and functionality, making the newsletter easy to maintain and extend over time.