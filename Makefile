all: run

db:
	docker-compose up -d
create_db:
	python hmtc/db.py


docker_build:
	docker build -t hmtc-app:latest .

docker_push:
	docker push mattsbitt/hmtc:latest

docker_save:
	docker image save -o hmtc-latest.tar mattsbitt/hmtc:latest
