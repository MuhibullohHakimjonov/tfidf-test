import re

token_pattern = re.compile(r'\b\w+\b')


def tokenize(text):
	return token_pattern.findall(text.lower())


def process_file_content(file_content):
	return tokenize(file_content.decode('utf-8', errors='ignore').strip())


def process_text(text):
	return tokenize(text)
