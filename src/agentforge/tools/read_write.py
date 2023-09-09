import os


def read_file(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
    return text


def write_file(folder, file, text, mode='a'):
    # Check if the folder exists. If not, create it.
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(os.path.join(folder, file), mode, encoding="utf-8") as f:
        f.write(text)

