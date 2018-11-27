FROM python:3-alpine
RUN pip3 install pipenv

RUN set -ex && mkdir /app
WORKDIR /app

COPY Pipfile .
COPY Pipfile.lock .

RUN set -ex && pipenv install --deploy --system

VOLUME /root/.cache
VOLUME /root/.config

COPY . .

ENTRYPOINT ["python3", "interlinker.py"]
