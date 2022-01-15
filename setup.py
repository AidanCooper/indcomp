import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="indcomp",
    version="0.1.0",
    description="Perform indirect treatment comparison (ITC) analyses",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/AidanCooper/indcomp",
    author="Aidan Cooper",
    author_email="aidan@aidancooper.co.uk",
    keywords=[
        "indirect",
        "treatment",
        "comparison",
        "MAIC",
        "STC",
        "ML-NMR",
        "adjusted",
    ],
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    packages=["indcomp"],
    include_package_data=True,
    install_requires=["numpy", "scipy", "pandas", "matplotlib"],
)
