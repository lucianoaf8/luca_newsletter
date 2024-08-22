# scripts\main.py
from utils.index_parser import load_html_and_inline_css
from utils.send_email import send_html_email

# Prepare the HTML content
html_content = load_html_and_inline_css(
    "index.html"
)

# Send the email
send_html_email("lucianoaf8@gmail.com; davidkennedy95@hotmail.com", "Luca Newsletter", html_content)
