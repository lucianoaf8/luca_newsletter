import logging
from bs4 import BeautifulSoup

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

html_file_path = r'C:\Projects\luca_newsletter_restructure\build\index.html'
css_folder_path = r'C:\Projects\luca_newsletter_restructure\build\css'
output_mjml_file = r'C:\Projects\luca_newsletter_restructure\build\output.mjml'

# List of all CSS files
css_files = [
    'arts.css', 'breathing_box.css', 'challenge.css', 'english_luca.css', 
    'finance_highlights.css', 'footer.css', 'fun_fact.css', 'header.css', 
    'highlight_section.css', 'history.css', 'joke.css', 'main.css', 
    'motivational_gif.css', 'motivational_quote.css', 'news.css', 'weather_widget.css'
]

# Mapping HTML tags to MJML tags
tag_mapping = {
    'div': 'mj-section',
    'h1': 'mj-text',
    'h2': 'mj-text',
    'h3': 'mj-text',
    'h4': 'mj-text',
    'h5': 'mj-text',
    'h6': 'mj-text',
    'p': 'mj-text',
    'img': 'mj-image',
    'a': 'mj-button',
    'section': 'mj-section',
    'span': 'mj-text',  # span converted to mj-text for inline styling
    'ul': 'mj-text',  # lists are handled as text in MJML
    'li': 'mj-text',  # each list item is treated as text in MJML
    'table': 'mj-table',  # table converted to mj-table for data presentation
}

# Function to convert an HTML element and its children to MJML
def convert_element_to_mjml(element):
    if element.name is None:  # Text node
        return str(element)

    mjml_tag = tag_mapping.get(element.name, element.name)  # Default to same tag if not in mapping
    logging.info(f"Converting <{element.name}> to <{mjml_tag}>")
    
    # Build MJML tag with its attributes
    attributes = ' '.join(f'{k}="{v}"' for k, v in element.attrs.items())
    content = ''.join(convert_element_to_mjml(child) for child in element.children)

    return f'<{mjml_tag} {attributes}>{content}</{mjml_tag}>'

# Function to apply CSS as MJML attributes or inline styles
def apply_css_styles(element, css_rules):
    try:
        if element.name == 'img':
            element['width'] = "100px"  # Set default width for images
            logging.info(f"Applied width for <img>")

        # Inline styles to attributes conversion for MJML
        if element.name in ['h1', 'h2', 'p']:
            font_size = element.get('style', {}).get('font-size', '20px')
            element['font-size'] = font_size  # Applying font-size as MJML attribute
            logging.info(f"Converted inline styles for {element.name}")

    except Exception as e:
        logging.error(f"Error applying CSS to tag <{element.name}>: {str(e)}")

# Load and parse the HTML
def load_html_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        logging.info("Loaded HTML file successfully")
        return soup
    except Exception as e:
        logging.error(f"Failed to load HTML file: {str(e)}")
        return None

# Parse CSS file and return rules as dictionary
def parse_css_file(css_file):
    try:
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        rules = []
        for line in css_content.splitlines():
            if '{' in line:
                selector = line.split('{')[0].strip()
                attributes = {}
                content = line.split('{')[1].split('}')[0].strip()
                for attr in content.split(';'):
                    if ':' in attr:
                        key, value = attr.split(':')
                        attributes[key.strip()] = value.strip()
                rules.append((selector, attributes))
        logging.info(f"Parsed CSS file {css_file}")
        return rules
    except Exception as e:
        logging.error(f"Error parsing CSS file {css_file}: {str(e)}")
        return []

# Main conversion function
def convert_to_mjml(html_file_path, css_folder_path, output_mjml_file):
    try:
        soup = load_html_file(html_file_path)
        if not soup:
            return
        
        # Parse each CSS file
        css_rules = []
        for css_file in css_files:
            css_rules.extend(parse_css_file(f'{css_folder_path}/{css_file}'))

        # Apply CSS styles and convert elements
        converted_content = ""
        for element in soup.find_all(True):
            logging.info(f"Processing tag: <{element.name}>")
            apply_css_styles(element, css_rules)
            converted_content += convert_element_to_mjml(element)

        # Wrap the content in MJML tags
        mjml_structure = f"""<mjml>
        <mj-head>
            <mj-title>Luca Newsletter</mj-title>
        </mj-head>
        <mj-body>{converted_content}</mj-body>
        </mjml>"""

        # Write the MJML content to the output file
        with open(output_mjml_file, 'w', encoding='utf-8') as f:
            f.write(mjml_structure)
            logging.info(f"Successfully wrote MJML content to {output_mjml_file}")
    
    except Exception as e:
        logging.error(f"Conversion process failed: {str(e)}")

# Run the converter with enhanced error handling and logging
convert_to_mjml(html_file_path, css_folder_path, output_mjml_file)
