"""Setup script for wheelchair_controller package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wheelchair-bot",
    version="0.1.0",
    author="Wheelchair-Bot Contributors",
    description="Interface for controlling popular electric wheelchairs using game controllers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mrhegemon/Wheelchair-Bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Hardware",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No hard dependencies - RPi.GPIO only needed on actual hardware
    ],
    extras_require={
        "rpi": ["RPi.GPIO>=0.7.1"],
        # `keyboard` extra removed in audit gap G-22 — see
        # wheelchair_controller/keyboard_control.py for the rationale.
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
