from setuptools import setup, find_packages

setup(
    name = "Math String to Operation",
    version = "1.0",
    description = "Converts math strings into Python function operations.",
    author = "Ezra Oppenheimer",
    author_email = "ezra.oppenheimer@gmail.com",
    packages = find_packages(),  # Same as name
    install_requires = [],  # External packages as dependencies
)