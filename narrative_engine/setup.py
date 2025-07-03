#!/usr/bin/env python3
"""
Setup script for The Narrative Engine
A modular, domain-agnostic AI-driven narrative architecture
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "The Narrative Engine - A modular, domain-agnostic AI-driven narrative architecture"

# Read requirements from requirements.txt if it exists
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="narrative-engine",
    version="0.1.0",
    author="Stephen John Miller",
    author_email="",  # Add if available
    description="A domain-agnostic storytelling framework with layered memory, context modeling, and narrative continuity management.",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="",  # Add repository URL if available
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Artistic Software",
        "Topic :: Games/Entertainment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=[
        # "openai>=1.0.0",  # Removed - using Ollama instead
        "numpy>=1.21.0",
        "pydantic>=2.0.0",
        "python-dotenv>=0.19.0",
        "requests>=2.25.0",
        "typing-extensions>=4.0.0",
        "dataclasses-json>=0.5.0",
        "uuid>=1.30",
    ],
    extras_require={
        "vector": [
            "faiss-cpu>=1.7.0",
            "sentence-transformers>=2.0.0",
        ],
        "web": [
            "flask>=2.0.0",
            "flask-cors>=3.0.0",
        ],
        "cache": [
            "redis>=4.0.0",
        ],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.900",
        ],
        "all": [
            "faiss-cpu>=1.7.0",
            "sentence-transformers>=2.0.0",
            "flask>=2.0.0",
            "flask-cors>=3.0.0",
            "redis>=4.0.0",
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.900",
        ],
    },
    include_package_data=True,
    package_data={
        "narrative_engine": [
            "docs/*.md",
            "memory/requirements-vector.txt",
        ],
    },
    entry_points={
        "console_scripts": [
            "narrative-engine=narrative_engine.core.narrative_engine:main",
        ],
    },
    keywords=[
        "narrative",
        "storytelling",
        "ai",
        "memory",
        "emotional",
        "interactive",
        "gaming",
        "therapy",
        "education",
        "fiction",
    ],
    project_urls={
        "Documentation": "",  # Add if available
        "Source": "",  # Add if available
        "Tracker": "",  # Add if available
    },
)
