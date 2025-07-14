# setup.py
from setuptools import setup, find_packages

setup(
    name="pucp-cli",
    version="1.0.0",
    description="CLI para PUCP Cloud Orchestrator",
    author="Tu Nombre",
    author_email="tu.email@pucp.edu.pe",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0",
        "requests>=2.28.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "pucp=pucp_cli.main:cli",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)