import os


# security: check the path is inside the expected limit
# raises an exception if it's out of bounds
def check_path(file_path: str, expected_base: str):
    abs_path = os.path.abspath(file_path)
    if not abs_path.startswith(expected_base):
        raise ValueError("invalid file path")
