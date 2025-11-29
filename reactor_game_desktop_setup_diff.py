--- reactor_game_desktop/setup.py (原始)


+++ reactor_game_desktop/setup.py (修改后)
from setuptools import setup, find_packages

setup(
    name="reactor-game",
    version="1.0.0",
    description="A desktop version of the REACTOR strategy game",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Reactor Game Developer",
    author_email="",
    url="",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "reactor-game=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.6",
)