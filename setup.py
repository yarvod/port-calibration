from setuptools import setup, find_packages
from io import open


def read(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()


setup(
    name="port-calibration",
    version="0.12",
    description="SIS calibration",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="yarvod",
    author_email="ya.vodzyanovskiy@lebedev.ru",
    url="https://github.com/yarvod/port-calibration",
    keywords="port calibration vna",
    packages=find_packages(),
    install_requires=["numpy"],
)