import os


def generate_base_project():
    with open("lifeguard_settings.py", "w") as settings_file:
        settings_file.write(
            """
PLUGINS = []

def setup(_lifeguard_context):
    pass
"""
        )
    if not os.path.exists("validations"):
        os.makedirs("validations")
