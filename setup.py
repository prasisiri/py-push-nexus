"""Setup script for connect-postgres-utility."""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="connect-postgres-utility",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description="A PostgreSQL connection utility for AWS RDS with environment-aware credential management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Organization",
    author_email="your-email@example.com",
    url="https://github.com/your-org/connect-postgres-utility",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "psycopg2-binary>=2.9.0",
        "configparser>=5.0.0",
        "hvac>=1.0.0",
        "boto3>=1.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ]
    },
    include_package_data=True,
    zip_safe=False,
) 