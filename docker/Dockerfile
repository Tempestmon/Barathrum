ARG PYTHON_VERSION=3.10
#TODO: Сделать пользователя с ограниченными правами и работать из под него

FROM python:${PYTHON_VERSION}-slim as build

WORKDIR /home

COPY /barathrum /home/barathrum
COPY poetry.lock pyproject.toml run.py /home/

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends gcc && \
    python -m pip install --upgrade pip && \
    pip install poetry gunicorn --no-cache-dir && \
    poetry install

EXPOSE 5000

ENTRYPOINT ["poetry", "run", "python"]
CMD ["run.py"]