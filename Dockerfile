FROM python:3.11-slim

RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 -ms /bin/bash appuser

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

USER appuser
WORKDIR /home/appuser

ENV VIRTUAL_ENV="/home/appuser/venv"
ENV PATH="${PATH}:/home/appuser"
ENV PATH="${PATH}:/home/appuser/.local/bin"
ENV PATH="${PATH}:/home/appuser/venv/bin"
ENV PYTHONPATH="${PYTHONPATH}:/home/appuser/task_whisperer"


COPY requirements.txt requirements.txt
RUN python -m pip install uv && uv venv /home/appuser/venv
RUN uv pip install -r requirements.txt

COPY task_whisperer /home/appuser/task_whisperer

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "/home/appuser/task_whisperer/streamlit_app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
