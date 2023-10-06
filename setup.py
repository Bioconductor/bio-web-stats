from setuptools import setup, find_packages

setup(
    name="bio-web-stats",
    packages=find_packages(where="app"),
    package_dir={"": "app"}
)
