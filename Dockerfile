FROM python:3.9.7
WORKDIR /usr/src/app


RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install tesseract-ocr -y

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV FLASK_APP='server'
ENV FLASK_ENV='development'

EXPOSE 80
CMD [ "-m", "flask", "run", "--host=0.0.0.0", "--port=80" ]
ENTRYPOINT ["python3"]
