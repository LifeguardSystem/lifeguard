"""
Lifeguard Helpers
"""


def load_implementation(implementation):
    """
    Load and create instance from a string to class
    """
    package_path = implementation.split(".")
    class_name = package_path.pop(-1)
    return getattr(__import__(".".join(package_path)), class_name)()
