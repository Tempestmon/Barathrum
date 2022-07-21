FROM python:3.10-slim as build

WORKDIR /barathrum

COPY . /barathrum

RUN apt-get update -y && \
    apt-get install -y libzbar-dev && \
    python -m pip install --upgrade pip && \
    pip install poetry --no-cache-dir && \
    poetry install

EXPOSE 5000

ENTRYPOINT ["poetry"]
CMD ["run", "python", "barathrum/app.py"]