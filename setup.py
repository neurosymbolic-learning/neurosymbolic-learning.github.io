import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="neurosym",
    version="0.1.0",
    author="Kavi Gupta",
    author_email="kavig+neurosym@mit.edu",
    description="Permanant cache.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kavigupta/neurosym-lib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[],
)
