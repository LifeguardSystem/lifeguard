from setuptools import setup, find_packages

setup(
    name="lifeguard",
    version="0.0.9",
    url="https://github.com/LifeguardSystem/lifeguard",
    author="Diego Rubin",
    author_email="contact@diegorubin.dev",
    license="GPL2",
    scripts=["bin/lifeguard"],
    include_package_data=True,
    description="Application to monitor your systems and give you the security to sleep peacefully at night",
    install_requires=["flask", "schedule", "gunicorn", "requests"],
    classifiers=["Development Status :: 3 - Alpha"],
    packages=find_packages(),
)
