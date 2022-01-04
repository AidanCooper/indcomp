import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="indirectcomp",
    version="0.1.0",
    description="Performs indirect comparison analyses",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/AidanCooper/indirectcomp",
    author="Aidan Cooper",
    author_email="aidan@aidancooper.co.uk",
    keywords=["indirect", "treatment", "comparison", "MAIC", "adjusted"],
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    packages=["indirectcomp"],
    include_package_data=True,
    install_requires=[],
)
