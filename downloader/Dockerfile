FROM python:3

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR /usr/src/app


COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache \
    pip3 install -r requirements.txt


ENV PYTHONPATH="${PYTHONPATH}:/usr/src/app"

CMD [ "src/main.py", "consumer", "--bootstrap_server=kafka:9092" , "--topic=frames" ]
ENTRYPOINT ["python3"]
