all: run

dev_db:
	docker-compose -f ~/programming/docker/docker-compose.yaml up -d


docker_save:
	docker image save -o hmtc-latest.tar mattsbitt/hmtc:latest
