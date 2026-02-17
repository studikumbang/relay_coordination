"""
relay_coordination setup script
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="relay_coordination",
    version="1.0.1",
    author="Relay Coordination Team",
    description="ETAP-style relay coordination simulation for pandapower",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/relay_coordination",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandapower",
        "numpy",
        "pandas",
        "matplotlib",
    ],
)
