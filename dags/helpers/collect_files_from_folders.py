import os

def collect_files_from_folders(path):
    files = os.listdir(path)
    return files


def collect_files_paths_from_folders(path):
    files = os.listdir(path)
    full_paths = []
    for file in files:
        full_path = os.path.join(path, file)
        full_paths.append(full_path)
    return full_paths