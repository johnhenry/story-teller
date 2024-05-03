from pathlib import Path
import logging
import glob
logging.basicConfig(level=logging.ERROR)

def log_error(message):
  logging.error(message)

def read_file(file_path):
  try:
    return Path(file_path).read_text()
  except FileNotFoundError:
    return None

def write_file(file_path, text):
  try:
    Path(file_path).write_text(text)
    return text
  except Exception as e:
    log_error(f"File Error {file_path}: {e}")
    return None

def glob_count(pattern):
    return len(glob.glob(pattern))
