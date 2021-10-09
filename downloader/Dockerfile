FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

CMD [ "python3", "src/main.py", "consumer", "--bootstrap_server=kafka:9092" , "--topic=frames" ]
