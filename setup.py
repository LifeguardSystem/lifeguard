from setuptools import setup, find_packages
from lifeguard import VERSION

setup(
    name="lifeguard",
    version=VERSION,
    url="https://github.com/LifeguardSystem/lifeguard",
    author="Diego Rubin",
    author_email="contact@diegorubin.dev",
    license="GPL2",
    scripts=["bin/lifeguard", "bin/lifeguard-server", "bin/lifeguard-scheduler"],
    include_package_data=True,
    description="Application to monitor your systems and give you the security to sleep peacefully at night",
    install_requires=["flask", "schedule", "gunicorn", "requests"],
    classifiers=["Development Status :: 3 - Alpha"],
    packages=find_packages(),
)
