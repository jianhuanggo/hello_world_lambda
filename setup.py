from setuptools import setup, find_packages

setup(
    name="crypto_info",
    version="1.0.0",
    description="Cryptocurrency Information System with MCP Integration",
    author="Devin AI",
    author_email="devin-ai-integration[bot]@users.noreply.github.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.28.0",
        "fastapi>=0.95.0",
        "uvicorn>=0.22.0",
        "pydantic>=1.10.0",
        "boto3>=1.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.3.1",
            "pytest-cov>=4.1.0",
        ],
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "crypto-info=crypto_info.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
