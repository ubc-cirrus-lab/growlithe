from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as r:
    requirements = r.read()

setup(
    name="growlithe",
    version="0.0.1",
    description="",
    packages=[package for package in find_packages() if package.startswith("src")],
    entry_points={"console_scripts": ["growlithe=src.main:main"]},
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ubc-cirrus-lab/serverless-compliance",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements.split("\n"),
    python_requires=">=3.11",
)