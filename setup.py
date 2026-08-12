import os
from typing import List
from setuptools import setup, find_packages

# Target string for local package editable mode
HYPHEN_E_DOT = "-e ."

def get_requirements(file_path: str) -> List[str]:
    """
    Read requirements.txt from a file and return them as a list of dependencies.
    """
    requirements = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file_obj:
            # Use strip() to remove \r, \n, and extra whitespace.
            requirements = [req.strip() for req in file_obj.readlines()]

            # Remove blank lines or comment lines
            requirements = [req for req in requirements if req and not req.startswith("#")]

            # Remove '-e .' from requirements if present
            if HYPHEN_E_DOT in requirements:
                requirements.remove(HYPHEN_E_DOT)
                
    return requirements

setup(
    name="E-COMMERCE-ANALYTICS-ML-PIPELINE",
    version="0.0.1",
    author="John",
    author_email="johnquang2004@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements("requirements.txt"),
)