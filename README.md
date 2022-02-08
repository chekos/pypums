# pypums

<div align="center">

[![Build status](https://github.com/chekos/pypums/workflows/build/badge.svg?branch=master&event=push)](https://github.com/chekos/pypums/actions?query=workflow%3Abuild)
[![Changelog](https://img.shields.io/github/v/release/chekos/pypums?include_prereleases&label=changelog)](https://github.com/chekos/pypums/releases)
[![License](https://img.shields.io/github/license/chekos/pypums)](https://github.com/chekos/pypums/blob/master/LICENSE)

Download Public Use Micro Sample (PUMS) data files from the US Census Bureau's FTP server.
</div>

Usage
=====

To use PyPUMS in a project:

![on a jupyter notebook](https://github.com/chekos/pypums/blob/master/static/usage.gif?raw=true)

or as a CLI

![as a CLI](https://github.com/chekos/pypums/blob/master/static/cli.gif?raw=true)

## Installation

Install this library using `pip`:

    $ pip install pypums

## Usage

Usage instructions go here.

## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:

    cd pypums
    python -m venv venv
    source venv/bin/activate

Or if you are using `pipenv`:

    pipenv shell

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest

## 📃 Citation

```
@misc{pypums,
  author = {chekos},
  title = {Download Public Use Micro Sample (PUMS) data files from the US Census Bureau's FTP server.},
  year = {2020},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/chekos/pypums}}
}
```
