FROM python:3.9.7
WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install tesseract-ocr -y
RUN apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR /usr/src/app

COPY requirements.txt .
#RUN --mount=type=cache,target=/root/.cache \
RUN pip3 install -r requirements.txt

ENV PYTHONPATH="${PYTHONPATH}:/usr/src/app"

CMD [ "src/main.py", "consumer", "--bootstrap_server=kafka:9092" , "--topic=frames" ]
ENTRYPOINT ["python3"]
