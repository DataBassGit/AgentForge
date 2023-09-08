import os


def read_file(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
    return text


def write_file(folder, file, text):
    with open(os.path.join(folder, file), "a", encoding="utf-8") as f:
        f.write(text)
