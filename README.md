# setup
Docker config:
Docker buildkit must be enabled for python packages caching (Docker GUI -> Preferences -> Docker Engine)

https://docs.docker.com/develop/develop-images/build_enhancements/

Full data reset:
sudo docker-compose down
rm -rf ./data/*
sudo docker-compose build
sudo docker-compose up -d zookeeper
sudo docker-compose up -d kafka && sleep 5
sudo docker-compose up -d && sleep 5
sudo docker-compose exec web python3 -m src.db_init create_db
sudo docker-compose exec web python3 -m src.db_init kafka_init
sudo docker-compose ps

Debug image web:
cd ./web
sudo docker build -t web .
sudo docker run -it \
    -v $(pwd):/usr/src/app \
    -v $(pwd)/../shared:/usr/src/app/src/shared \
    -v $(pwd)/../data/frames:/data/frames \
    -p 80:80 \
    web src/server.py


Debug image downloader:
cd ./downloader
sudo docker build -t downloader .
sudo docker run -it \
    -v $(pwd):/usr/src/app \
    -v $(pwd)/../shared:/usr/src/app/src/shared \
    -v $(pwd)/../data/frames:/data/frames \
    downloader src/main.py


Debug image recognizer:
cd ./recognizer
sudo docker build -t recognizer .
sudo docker run -it \
    -v $(pwd):/usr/src/app \
    -v $(pwd)/../shared:/usr/src/app/src/shared \
    -v $(pwd)/../data/frames:/data/frames \
    recognizer src/main.py

https://eduardovra.github.io/building-two-sample-apps-using-hotwire-and-flask/