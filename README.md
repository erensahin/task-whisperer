# Task Whisperer

Welcome to Task Whisperer: Your Ultimate Task Description Assistant!

## Why Task Whisperer?

TaskWhisperer is your one-stop solution for crafting detailed and precise task
descriptions with ease. Say goodbye to tedious manual task creation and hello
to streamlined workflows and increased productivity!

## Features

- 🔍 Seamlessly Fetch Issues from Issue Tracking Systems. Currently, JIRA is supported.
- 🚀 Generate Embeddings from Issue Descriptions to prepare for LLM-based task generation.
- 🔮 Input a task summary and watch the magic happen with a single click!
- 📝 Review and edit generated task descriptions and submit to ITS with a single click!

## How to Use Task Whisperer

### Running Locally

#### Using Docker (Recommended)

It is strongly advised to use docker for running task whisperer locally.

Firstly, build the docker image:

``docker build . -t task_whisperer``

Then, run the container:

``docker run task_whisperer``

You can use the app by navigating to ``localhost:8501`` in your browser.

#### Using Local Development Environment

##### Create a Virtual Environment using uv

If you are a uv user (a brand new Python package installer)

Create a virtual environment (at .venv):

``uv venv``

Activate the virual environment (On macOS and Linux)

``source .venv/bin/activate``

Activate the virual environment (On Windows)

``.venv\Scripts\Activate``

Install the requirements:

``uv pip install -r requirements.txt```

##### Create a virtual environment using Python's venv

Create a virtual environment (On macOS and Linux)

``python -m venv path/to/my/venv``

Activate the virual environment (On macOS and Linux)

``source path/to/my/venv/bin/activate``

Create a virtual environment (On Windows)

``python -m venv path\to\my\venv``

Activate the virual environment (On Windows)

``source path\to\my\venv\Scripts\activate.bat``

