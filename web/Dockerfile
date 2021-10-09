FROM python:3.9.7
WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install tesseract-ocr -y

COPY ./requirements.txt requirements.txt
RUN pip3 install -r ./requirements.txt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=src/server
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=80
ENV DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres
ENV PYTHONPATH="${PYTHONPATH}:/usr/src/app"
EXPOSE 80

#CMD [ "ls", "-lr", "src"]
#
CMD [ "-m", "flask", "run"]
ENTRYPOINT ["python3"]

