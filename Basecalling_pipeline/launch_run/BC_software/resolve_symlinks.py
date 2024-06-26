import os

def get_real_path(path):
    if os.path.islink(path):
        real_path = os.path.realpath(path)
        return real_path
    else:
        return path

def resolve_symlinks(directory):
    real_paths = []
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            real_paths.append(get_real_path(filepath))

    return real_paths

