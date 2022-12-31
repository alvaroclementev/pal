# pal
Your Personal Activity Log

Your activity log is a lightweight record of the tasks that you have performed
over time.
It is a `git log` inpired tool to record any type of tasks.

This means that a record can have a title, and a body.

## Usage

**TODO**: Figure out the UX for this
Run the executable: 
```sh
pal
```

## Installation

`pal` is available as a python package, so can install it with: 

```sh
pip install pal
```

**NOTE**: This does method does not work currently, use `poetry install` or `poetry install --without dev` for now. 

## Development

This package uses `poetry` and `pre-commit` as external development tools.

To get set up, make sure you have `poetry` [installed](https://python-poetry.org/docs/#installation).

Clone the respository and run: 

```sh
poetry install
```

Or if you need to install LSP dependencies, you can use the optional dependency group:
```sh
poetry install --with lsp
```

And it will setup everything you need to get started developing the project.

We also use `pre-commit` to manage pre commit hooks, making sure the commited code 
maitains some minimal quality standards.
Follow the [installation instructions](https://pre-commit.com/#installation), and then
just run the following commmand once at the root of the repo:

```sh
pre-commit install
```

This will install the pre commit hooks, and now every commit will be checked against some code automated style checks.
By default it will only run on the minimum set of files (based on changes that are being commited), but you can force it to run the checks on all the files with:
```sh
pre-commit run --all-files
```
