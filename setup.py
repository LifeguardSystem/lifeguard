from setuptools import find_packages, setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="lifeguard",
    version="1.3.0",
    url="https://github.com/LifeguardSystem/lifeguard",
    author="Diego Rubin",
    author_email="contact@diegorubin.dev",
    license="GPL2",
    scripts=["bin/lifeguard"],
    include_package_data=True,
    description="Application to monitor your systems and give you the security to sleep peacefully at night",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "flask",
        "schedule",
        "gunicorn",
        "requests",
        "tabulate",
        "PyYAML",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Monitoring",
    ],
    packages=find_packages(),
)
