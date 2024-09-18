all: run

dev_db:
	docker-compose -f ~/programming/docker/docker-compose.yaml up -d

staging:
	docker-compose up --build

docker_save:
	docker image save -o hmtc-latest.tar mattsbitt/hmtc:latest

deploy:
	docker image tag hmtc-app:latest mattsbitt/hmtc:latest
	docker save mattsbitt/hmtc:latest | ssh -C root@192.168.0.202 docker load
cleanup:
	ruff check --config hmtc/config/ruff.toml . --fix
	black .

