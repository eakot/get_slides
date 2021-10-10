FROM python:3

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install tesseract-ocr -y

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

ENV PYTHONPATH="${PYTHONPATH}:/usr/src/app"

CMD [ "src/main.py", "consumer", "--bootstrap_server=kafka:9092" , "--topic=frames" ]
ENTRYPOINT ["python3"]
