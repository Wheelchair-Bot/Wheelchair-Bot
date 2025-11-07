"""Setup script for wheelchair_controller package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wheelchair-controller",
    version="1.0.0",
    author="Wheelchair-Bot Project",
    description="Raspberry Pi controller for wheelchair robot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mrhegemon/Wheelchair-Bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Hardware",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No hard dependencies - RPi.GPIO only needed on actual hardware
    ],
    extras_require={
        "rpi": ["RPi.GPIO>=0.7.1"],
        "keyboard": ["keyboard>=0.13.5"],
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pylint>=3.0.0",
            "black>=23.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wheelchair-controller=main:main",
        ],
    },
    include_package_data=True,
)
