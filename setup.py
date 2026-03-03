"""Setup configuration for tf-starter CLI tool."""

from setuptools import setup, find_packages

setup(
    name="tf-starter",
    version="1.0.0",
    description="Enterprise-grade Terraform Infrastructure-as-Code project generator",
    author="DevOps Team",
    python_requires=">=3.9",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "tf_starter": ["templates/**/*"],
    },
    install_requires=[
        "questionary>=2.0.0",
        "jinja2>=3.1.0",
    ],
    entry_points={
        "console_scripts": [
            "tf-starter=tf_starter.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Code Generators",
        "Topic :: System :: Systems Administration",
    ],
)