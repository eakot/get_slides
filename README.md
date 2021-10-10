# setup
Create the tables:
sudo docker-compose exec web python3 -m src.db_init create_db

Debug image web:
cd ./web
sudo docker build -t web .
sudo docker run -it -v $(pwd):/usr/src/app web src/server.py


Debug image downloader:
cd ./downloader
sudo docker build -t downloader .
sudo docker run -it -v $(pwd):/usr/src/app downloader src/main.py


https://eduardovra.github.io/building-two-sample-apps-using-hotwire-and-flask/