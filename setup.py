"""Setup configuration for Holberton Jr. Code Studio."""

from setuptools import setup, find_packages

setup(
    name="holberton-jr",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.5.0",
        "PyQt6-QScintilla>=2.14.0",
    ],
    entry_points={
        "console_scripts": [
            "holberton-jr=holberton_jr.main:main",
        ],
    },
    author="Holberton School",
    description="A beginner-friendly Python editor for kids ages 10-14",
    python_requires=">=3.8",
)