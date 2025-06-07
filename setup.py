from setuptools import setup, find_packages

setup(
    name="natuurspotter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "requests",
        "beautifulsoup4",
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "reportlab",
        "python-dotenv",
        "geopy",
        "wikipedia",
        "sqlalchemy",
    ],
    author="Yorbe van der Mast",
    author_email="yorbevandermast@proton.me",
    description="Kever-NatuurSpotter",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Yorb1431/ExamenScripting-NatuurSpotter",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 