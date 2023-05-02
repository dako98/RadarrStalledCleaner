from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh]
    print(requirements)

setup(
    name="RadarrStalledCleaner",
    version="1.2",
    author="Dako Dimov, Lyuboslav Angelov",
    author_email="",
    description="A Python project to clean stalled downloads from Radarr",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Users",
        "Programming Language :: Python :: 3.9.13",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9.13",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=3.7",
        ],
    },
)
