"""Setup python project.

References:
    [1] : https://xebia.com/blog/a-practical-guide-to-using-setup-py/
"""
from setuptools import find_packages, setup


def readme():
    with open('README.md', encoding='utf-8') as f:
        content = f.read()
    return content


def parse_requirements():
    with open("requirements.txt", "r") as f:
        return f.read().splitlines()


setup(
    name="icon-visualization-examples",
    packages=find_packages(include=["src"]),
    version='0.1.0',
    long_description=readme(),
    install_requires=parse_requirements(),
    author='See AUTHORS.md',
    author_email="frazier@iap-kborn",
    license='BSD-3-Clause'
)
