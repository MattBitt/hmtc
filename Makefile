all: run

create_db:
	python hmtc/db.py


docker_build:
	docker build -t mattsbitt/hmtc:latest .

docker_push:
	docker push mattsbitt/hmtc:latest
