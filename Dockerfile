FROM kennethreitz/pipenv
COPY . /app
ENTRYPOINT ["python3", "interlinker.py"]
