import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(
    name = "pyspec",
    version = "0.0.1",
    author = "Benjamin Hodgson",
    author_email = "benjamin.hodgson@huddle.net",
    url = "https://github.com/benjamin-hodgson/PySpec",
    description = "PySpec is a test runner for Python. It lets you write your tests in the style of C#'s Machine.Specifications.",
    package_dir = {'':'src'},
    packages = find_packages('src'),
    tests_require = ["sure >= 1.2.2"]
)
