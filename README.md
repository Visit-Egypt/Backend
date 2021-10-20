# Visit Egypt

## Description

Visit Egypt aplication made with Python's FastAPI framework and Hexagonal Architecture.


## Overview

This project is comprised of the following languages and libraries:

* Language: [Python 3.9+](https://www.python.org/)
* Web framework: [FastAPI](https://fastapi.tiangolo.com/)
* Production web server: [Uvicorn](http://www.uvicorn.org/)
* MongoDB database: [MongoDB](https://www.mongodb.com/)
* Password hashing utilities: [Passlib](https://passlib.readthedocs.io/)
* Data parsing and validation: [Pydantic](https://pydantic-docs.helpmanual.io/)
* Testing: [Pytest](https://docs.pytest.org/en/latest/)
* Linter: [Flake8](https://flake8.pycqa.org/en/latest/)
* Static type checker: [Mypy](https://mypy.readthedocs.io/en/stable/index.html)
* Formatter: [Black](https://github.com/psf/black)

## Development

To start development it is recommended to have these utilities installed in a local development machine:

* [Python 3.9+](https://www.python.org/)
* [Docker](https://www.docker.com/)
* [Git](https://git-scm.com/)

For better development experience, it is recommended these tools:

* [Visual Studio Code](https://code.visualstudio.com/)

### Running the API

To run the API in development mode, follow these steps:

* Test the API with: `pytest`
* Format code with: `autopep8 --in-place --recursive visitegypt`
* Lint the code with: `flake8 todolist tests`
* Run static analysis with: `mypy job_form_api tests`

