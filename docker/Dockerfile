FROM python:3.10-slim as build

WORKDIR /barathrum

COPY . /barathrum

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends gcc && \
    python -m pip install --upgrade pip && \
    pip install poetry gunicorn --no-cache-dir && \
    poetry install

EXPOSE 5000

ENTRYPOINT ["poetry"]
CMD ["run", "python", "barathrum/app.py"]