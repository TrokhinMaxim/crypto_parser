import os
from bs4 import BeautifulSoup
import re


def parse_telegram_html(html_file_name):
    app_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(app_directory, 'data', html_file_name)

    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    messages = soup.find_all('div', {'class': 'text'})
    filtered_messages = [msg.text for msg in messages]

    output_file_path = os.path.join(app_directory, 'data', 'filtered_messages.txt')
    with open(output_file_path, 'w', encoding='utf-8') as file:
        for msg in filtered_messages:
            file.write(f"{msg}\n")


def extract_latin_and_digits(file_path):
    latin_and_digits = []

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            words = re.findall(r'\b[a-zA-Z0-9]+\b', line)
            latin_and_digits.extend(words)

    return latin_and_digits
