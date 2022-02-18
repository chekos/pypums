import os
from setuptools import setup


VERSION = "0.1rc1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="pypums",
    description="Download Public Use Micro Sample (PUMS) data files from the US Census Bureau's FTP server.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Sergio Sanchez",
    url="https://github.com/chekos/pypums",
    project_urls={
        "Issues": "https://github.com/chekos/pypums/issues",
        "CI": "https://github.com/chekos/pypums/actions",
        "Changelog": "https://github.com/chekos/pypums/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["pypums"],
    install_requires=[
        "us>=2.0.2",
        "httpx>=0.22.0",
        "pandas>=1.1.0",
        "rich>=11.0.0",
        "typer>=0.4.0",
    ],
    extras_require={
        "test": ["pytest"],
        "docs": ["mkdocs", "mdx_include", "mkautodoc", "pymdown-extensions"],
    },
    python_requires=">=3.6",
    entry_points="""
        [console_scripts]
        pypums=pypums.cli:cli
    """,
)
