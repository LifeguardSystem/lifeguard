"""Genral Utility Functions
"""
import os


def build_import(path, cur_name):
    """Returns python like import name"""
    head, tail = os.path.split(path)
    if tail:
        cur_name = f"{tail}.{cur_name}"
        final_name = cur_name
    if head:
        final_name = build_import(head, cur_name)
    return final_name
