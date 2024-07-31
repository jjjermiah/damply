
# damply

[![codecov](https://codecov.io/gh/jjjermiah/damply/graph/badge.svg?token=tCcajRIGz9)](https://codecov.io/gh/jjjermiah/damply)
[![CI-CD](https://github.com/jjjermiah/damply/actions/workflows/main.yaml/badge.svg)](https://github.com/jjjermiah/damply/actions/workflows/main.yaml)
[![CodeFactor](https://www.codefactor.io/repository/github/jjjermiah/damply/badge)](https://www.codefactor.io/repository/github/jjjermiah/damply)

[![pixi-badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/prefix-dev/pixi/main/assets/badge/v0.json&style=flat-square)](https://github.com/prefix-dev/pixi)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&style=flat-square)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=flat-square)](https://github.com/astral-sh/ruff)
[![Built with Material for MkDocs](https://img.shields.io/badge/mkdocs--material-gray?logo=materialformkdocs&style=flat-square)](https://github.com/squidfunk/mkdocs-material)

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/damply)](https://pypi.org/project/damply/)
[![PyPI - Version](https://img.shields.io/pypi/v/damply)](https://pypi.org/project/damply/)
[![PyPI - Format](https://img.shields.io/pypi/format/damply)](https://pypi.org/project/damply/)
[![Downloads](https://static.pepy.tech/badge/damply)](https://pepy.tech/project/damply)

## Overview


DaMPly (Data Management Plan) is a Python module designed to streamline the process of managing and packaging directories.

This tool is particularly useful for archiving project directories while leaving behind a README file to provide context and instructions for future users.

## Features

View a project's `README`, with emphasized fields that follow the Data Management Plan (DMP) guidelines.
![img](assets/screenshot.png)

TODO
- [ ] README Check: Verifies the presence of a README file in the specified directory.
- [ ] User Interaction: Prompts the user for necessary information to enhance the archiving process.
- [ ] Directory Compression: Compresses all files and sub


## Development

This project uses [`pixi`](pixi.sh) for managing the development environment.
A set of convenient `tasks` are defined in the `pyproject.toml` file to streamline the development process.

The `build` feature contains the following tasks:

- `build`: Builds the package.
- `publish-pypi`: Publishes the package to the main PYPI repository.
- `publish-test`: Publishes the package to the TEST-PYPI repository.

For more details, view the [devnotes on pixi + hatch](devnotes/pixi-hatch-build.md).

